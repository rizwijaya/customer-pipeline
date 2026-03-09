"""Public exports for ingestion service components."""

from services.ingestion import (
    CustomerIngestionService,
    CustomerRepository,
    IngestionError,
    MockCustomerGateway,
    UpstreamServiceError,
)

__all__ = [
    "CustomerIngestionService",
    "CustomerRepository",
    "IngestionError",
    "MockCustomerGateway",
    "UpstreamServiceError",
]
