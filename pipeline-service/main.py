from __future__ import annotations

"""FastAPI entrypoint for ingesting and querying customer data."""

from fastapi import FastAPI, HTTPException, Query

from config import settings
from database import get_session, init_db
from models.customer import Customer
from schemas import (
    CustomerResponse,
    HealthResponse,
    IngestResponse,
    PaginatedCustomersResponse,
    as_customer_response,
)
from services.ingestion import (
    CustomerIngestionService,
    CustomerRepository,
    IngestionError,
    MockCustomerGateway,
    UpstreamServiceError,
)

app = FastAPI(title="Customer Pipeline Service")


def _build_ingestion_service(repository: CustomerRepository) -> CustomerIngestionService:
    """Create ingestion service with gateway settings from environment config."""
    gateway = MockCustomerGateway(
        base_url=settings.mock_server_url,
        page_size=settings.ingest_page_size,
    )
    return CustomerIngestionService(gateway=gateway, repository=repository)


@app.on_event("startup")
def startup() -> None:
    """Initialize database schema and SQL migrations when service starts."""
    init_db()


@app.post("/api/ingest", response_model=IngestResponse)
def ingest_customers() -> IngestResponse:
    """Ingest all customers from the mock server into the local database."""
    with get_session() as session:
        repository = CustomerRepository(session)
        service = _build_ingestion_service(repository)

        try:
            count = service.ingest()
            return IngestResponse(status="success", records_processed=count)
        except UpstreamServiceError as exc:
            raise HTTPException(status_code=502, detail=f"Mock server error: {exc}") from exc
        except IngestionError as exc:
            raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}") from exc


@app.get("/api/customers", response_model=PaginatedCustomersResponse)
def list_customers(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
) -> PaginatedCustomersResponse:
    """List stored customers from the database using pagination."""
    with get_session() as session:
        repository = CustomerRepository(session)
        total = repository.count()
        customers = repository.list_paginated(page=page, limit=limit)

    return PaginatedCustomersResponse(
        data=[as_customer_response(customer.to_dict()) for customer in customers],
        total=total,
        page=page,
        limit=limit,
    )


@app.get("/api/customers/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: str) -> CustomerResponse:
    """Return one stored customer by ID."""
    with get_session() as session:
        repository = CustomerRepository(session)
        customer: Customer | None = repository.get_by_id(customer_id)

    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    return as_customer_response(customer.to_dict())


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Service health endpoint for readiness/liveness checks."""
    return HealthResponse(status="ok")
