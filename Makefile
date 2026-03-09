SHELL := /bin/zsh

# Load environment from .env when available
ifneq (,$(wildcard ./.env))
include .env
export
endif

MOCK_BASE_URL ?= http://localhost:$(MOCK_SERVER_PORT)
PIPELINE_BASE_URL ?= http://localhost:$(PIPELINE_SERVICE_PORT)
APP_HOST ?= 0.0.0.0
APP_PORT ?= 8000

.PHONY: help up down logs ingest health test-api
.PHONY: local-setup-mock local-run-mock local-setup-pipeline local-run-pipeline local-test-api

help:
	@echo "Available targets:"
	@echo "  make up            - Build and start all services"
	@echo "  make down          - Stop services"
	@echo "  make logs          - Follow all logs"
	@echo "  make health        - Health check both APIs"
	@echo "  make ingest        - Trigger ingestion endpoint"
	@echo "  make test-api      - Health + ingest + list customers"
	@echo "  make local-setup-mock     - Setup mock-server venv/deps with uv (non-Docker)"
	@echo "  make local-run-mock       - Run mock-server locally with uv (non-Docker)"
	@echo "  make local-setup-pipeline - Setup pipeline-service venv/deps with uv (non-Docker)"
	@echo "  make local-run-pipeline   - Run pipeline-service locally with uv (non-Docker)"
	@echo "  make local-test-api       - Test local APIs (health + ingest + list)"

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

health:
	@echo "[mock-server] $(MOCK_BASE_URL)/api/health"
	@curl -sS "$(MOCK_BASE_URL)/api/health" && echo
	@echo "[pipeline-service] $(PIPELINE_BASE_URL)/api/health"
	@curl -sS "$(PIPELINE_BASE_URL)/api/health" && echo

ingest:
	@echo "POST $(PIPELINE_BASE_URL)/api/ingest"
	@curl -sS -X POST "$(PIPELINE_BASE_URL)/api/ingest" && echo

test-api: health ingest
	@echo "GET $(PIPELINE_BASE_URL)/api/customers?page=1&limit=5"
	@curl -sS "$(PIPELINE_BASE_URL)/api/customers?page=1&limit=5" && echo

local-setup-mock:
	cd mock-server && uv venv && . .venv/bin/activate && uv pip install -r requirements.txt

local-run-mock:
	cd mock-server && . .venv/bin/activate && uv run python app.py

local-setup-pipeline:
	cd pipeline-service && uv venv && . .venv/bin/activate && uv pip install -r requirements.txt

local-run-pipeline:
	cd pipeline-service && \
	. .venv/bin/activate && \
	uv run hypercorn main:app --bind "$(APP_HOST):$(APP_PORT)"

local-test-api:
	@echo "[mock-server] http://localhost:$${MOCK_SERVER_PORT:-5000}/api/health"
	@curl -sS "http://localhost:$${MOCK_SERVER_PORT:-5000}/api/health" && echo
	@echo "[pipeline-service] http://localhost:$${APP_PORT:-8000}/api/health"
	@curl -sS "http://localhost:$${APP_PORT:-8000}/api/health" && echo
	@echo "POST http://localhost:$${APP_PORT:-8000}/api/ingest"
	@curl -sS -X POST "http://localhost:$${APP_PORT:-8000}/api/ingest" && echo
	@echo "GET http://localhost:$${APP_PORT:-8000}/api/customers?page=1&limit=5"
	@curl -sS "http://localhost:$${APP_PORT:-8000}/api/customers?page=1&limit=5" && echo
