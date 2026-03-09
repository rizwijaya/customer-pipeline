from __future__ import annotations

"""Pydantic response schemas for API endpoints."""

from typing import Any

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health-check payload."""

    status: str


class IngestResponse(BaseModel):
    """Result payload for the ingestion endpoint."""

    status: str
    records_processed: int


class CustomerResponse(BaseModel):
    """Serialized customer payload exposed over API."""

    customer_id: str
    first_name: str
    last_name: str
    email: str
    phone: str | None
    address: str | None
    date_of_birth: str | None
    account_balance: float | None
    created_at: str | None


class PaginatedCustomersResponse(BaseModel):
    """Customer list payload with pagination metadata."""

    data: list[CustomerResponse]
    total: int
    page: int
    limit: int


class ErrorResponse(BaseModel):
    """Standard error payload schema."""

    detail: str


def as_customer_response(payload: dict[str, Any]) -> CustomerResponse:
    """Convert a plain dictionary into a validated customer response model."""
    return CustomerResponse(**payload)
