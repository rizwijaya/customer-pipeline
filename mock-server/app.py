from __future__ import annotations

"""Mock customer API used by the pipeline service during local development."""

import json
import os
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request
from dotenv import load_dotenv

app = Flask(__name__)

SERVICE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SERVICE_DIR.parent
load_dotenv(PROJECT_ROOT / ".env", override=False)
load_dotenv(SERVICE_DIR / ".env", override=False)

DATA_PATH = Path(__file__).resolve().parent / "data" / "customers.json"


class CustomerFileRepository:
    """Read customer records from a JSON file."""

    def __init__(self, data_path: Path) -> None:
        self.data_path = data_path

    def load_all(self) -> list[dict[str, Any]]:
        """Load the complete customer dataset from disk."""
        with self.data_path.open("r", encoding="utf-8") as file:
            return json.load(file)


class CustomerQueryService:
    """Provide query operations over customer data."""

    def __init__(self, repository: CustomerFileRepository) -> None:
        self.repository = repository

    def get_paginated(self, page: int, limit: int) -> dict[str, Any]:
        """Return one page of customer records with pagination metadata."""
        customers = self.repository.load_all()
        start = (page - 1) * limit
        end = start + limit
        return {
            "data": customers[start:end],
            "total": len(customers),
            "page": page,
            "limit": limit,
        }

    def get_by_id(self, customer_id: str) -> dict[str, Any] | None:
        """Return a customer by ID or ``None`` when not found."""
        customers = self.repository.load_all()
        return next((item for item in customers if item["customer_id"] == customer_id), None)


repository = CustomerFileRepository(DATA_PATH)
service = CustomerQueryService(repository)


@app.get("/api/health")
def health_check() -> tuple[dict[str, str], int]:
    """Basic health endpoint used by orchestration and checks."""
    return {"status": "ok"}, 200


@app.get("/api/customers")
def get_customers() -> tuple[Any, int]:
    """List customers with simple page and limit query parameters."""
    page = max(request.args.get("page", default=1, type=int), 1)
    limit = max(request.args.get("limit", default=10, type=int), 1)

    payload = service.get_paginated(page=page, limit=limit)
    return jsonify(payload), 200


@app.get("/api/customers/<customer_id>")
def get_customer(customer_id: str) -> tuple[Any, int]:
    """Fetch one customer by ID."""
    customer = service.get_by_id(customer_id)

    if customer is None:
        return jsonify({"error": "Customer not found"}), 404

    return jsonify(customer), 200


if __name__ == "__main__":
    app.run(
        host=os.getenv("MOCK_SERVER_HOST", "0.0.0.0"),
        port=int(os.getenv("MOCK_SERVER_PORT", "5000")),
    )
