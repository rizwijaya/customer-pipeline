from __future__ import annotations

"""Ingestion workflow: fetch customers from upstream and upsert into PostgreSQL."""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Protocol

import dlt
import requests
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from models.customer import Customer


class UpstreamServiceError(Exception):
    """Raised when the mock customer API cannot be reached or returns an error."""

    pass


class IngestionError(Exception):
    """Raised for non-upstream failures during ingestion."""

    pass


class CustomerGateway(Protocol):
    """Interface for services that can fetch customer records."""

    def fetch_all_customers(self) -> list[dict[str, Any]]:
        ...


class CustomerStore(Protocol):
    """Interface for persistence backends that can upsert customer records."""

    def upsert_many(self, records: list[dict[str, Any]]) -> int:
        ...


class MockCustomerGateway:
    """Fetch paginated customer data from the mock server."""

    def __init__(self, base_url: str, page_size: int = 10) -> None:
        self.base_url = base_url.rstrip("/")
        self.page_size = max(1, page_size)

    def _customers_resource(self) -> Any:
        """Build a dlt resource that lazily yields customer batches per page."""

        @dlt.resource(name="customers", primary_key="customer_id", write_disposition="merge")
        def customers_resource() -> Any:
            page = 1
            while True:
                response = requests.get(
                    f"{self.base_url}/api/customers",
                    params={"page": page, "limit": self.page_size},
                    timeout=15,
                )
                response.raise_for_status()

                payload = response.json()
                records = payload.get("data", [])
                if not records:
                    break

                yield records

                total = int(payload.get("total", 0))
                if page * self.page_size >= total:
                    break

                page += 1

        return customers_resource

    def fetch_all_customers(self) -> list[dict[str, Any]]:
        """Fetch all available customer records across upstream pages."""
        all_records: list[dict[str, Any]] = []
        resource = self._customers_resource()

        try:
            for batch in resource():
                if isinstance(batch, list):
                    all_records.extend(batch)
                else:
                    all_records.append(batch)
        except requests.RequestException as exc:
            raise UpstreamServiceError(str(exc)) from exc

        return all_records


class CustomerRepository:
    """Database persistence operations for customer entities."""

    def __init__(self, session: Session) -> None:
        self.session = session

    @staticmethod
    def _parse_customer(record: dict[str, Any]) -> dict[str, Any]:
        """Normalize raw payload values into database-compatible Python types."""
        parsed = dict(record)

        if parsed.get("date_of_birth"):
            parsed["date_of_birth"] = date.fromisoformat(parsed["date_of_birth"])

        if parsed.get("created_at"):
            parsed["created_at"] = datetime.fromisoformat(parsed["created_at"])

        if parsed.get("account_balance") is not None:
            parsed["account_balance"] = Decimal(str(parsed["account_balance"]))

        return parsed

    def upsert_many(self, records: list[dict[str, Any]]) -> int:
        """Insert or update customers in a single PostgreSQL upsert statement."""
        if not records:
            return 0

        normalized_records = [self._parse_customer(record) for record in records]
        stmt = insert(Customer).values(normalized_records)

        update_columns = {
            column.name: getattr(stmt.excluded, column.name)
            for column in Customer.__table__.columns
            if column.name != "customer_id"
        }

        stmt = stmt.on_conflict_do_update(
            index_elements=[Customer.customer_id],
            set_=update_columns,
        )

        self.session.execute(stmt)
        self.session.commit()
        return len(normalized_records)

    def count(self) -> int:
        """Return total number of stored customers."""
        return self.session.scalar(select(func.count()).select_from(Customer)) or 0

    def list_paginated(self, page: int, limit: int) -> list[Customer]:
        """Return one page of customers ordered by ID for stable pagination."""
        offset = (page - 1) * limit
        stmt = (
            select(Customer)
            .order_by(Customer.customer_id)
            .offset(offset)
            .limit(limit)
        )
        return list(self.session.scalars(stmt).all())

    def get_by_id(self, customer_id: str) -> Customer | None:
        """Return one customer by primary key."""
        return self.session.get(Customer, customer_id)


class CustomerIngestionService:
    """Coordinate customer fetch and persistence for ingestion endpoint."""

    def __init__(self, gateway: CustomerGateway, repository: CustomerStore) -> None:
        self.gateway = gateway
        self.repository = repository

    def ingest(self) -> int:
        """Fetch all upstream customers and persist them, returning record count."""
        try:
            records = self.gateway.fetch_all_customers()
            return self.repository.upsert_many(records)
        except UpstreamServiceError:
            raise
        except Exception as exc:  # pylint: disable=broad-except
            raise IngestionError(str(exc)) from exc
