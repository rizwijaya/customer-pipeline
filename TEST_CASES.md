# API Test Cases

This document defines API test scenarios for both services using a consistent format.

## Latest Execution Result (2026-03-08)

- Total test cases: `12`
- Passed: `12`
- Failed: `0`
- Overall status: `ALL PASS`

## Test Progress Summary

| Test Case ID | Endpoint | Method | Progress | Notes |
|---|---|---|---|---|
| TC-MOCK-001 | `/api/health` | GET | Success | Basic health check for Flask mock service. |
| TC-MOCK-002 | `/api/customers?page=1&limit=5` | GET | Success | Valid pagination for Flask list endpoint. |
| TC-MOCK-003 | `/api/customers?page=999&limit=5` | GET | Success | Out-of-range page should return empty `data`. |
| TC-MOCK-004 | `/api/customers/CUST-001` | GET | Success | Valid customer lookup in JSON source. |
| TC-MOCK-005 | `/api/customers/CUST-999` | GET | Success | Invalid customer lookup should return 404. |
| TC-PIPE-001 | `/api/health` | GET | Success | Basic health check for FastAPI service. |
| TC-PIPE-002 | `/api/ingest` | POST | Success | Ingestion should fetch, upsert, and return processed count. |
| TC-PIPE-003 | `/api/customers?page=1&limit=5` | GET | Success | Validate paginated DB query after ingestion. |
| TC-PIPE-004 | `/api/customers/CUST-001` | GET | Success | Valid customer lookup in DB. |
| TC-PIPE-005 | `/api/customers/CUST-999` | GET | Success | Invalid customer lookup should return 404. |
| TC-PIPE-006 | `/api/customers?page=0&limit=5` | GET | Success | Query validation should reject invalid `page`. |
| TC-PIPE-007 | `/api/customers?page=1&limit=101` | GET | Success | Query validation should reject invalid `limit` (>100). |

## Preconditions

1. Run services:

```bash
docker compose up -d --build
```

2. Ensure both services are healthy:

```bash
curl -X GET http://localhost:5000/api/health
curl -X GET http://localhost:8000/api/health
```

3. For DB query tests, trigger ingestion first:

```bash
curl -X POST http://localhost:8000/api/ingest
```

## Detailed Test Cases

### TC-MOCK-001

- **Endpoint Tested**: `/api/health`
- **Method**: `GET`
- **Description**: Verify Flask mock service health endpoint is reachable.
- **Request**:
  ```bash
  curl -X GET http://localhost:5000/api/health
  ```
- **Expected Response**:
  - Status: `200 OK`
  - Body:
    ```json
    {"status":"ok"}
    ```
- **Progress**: Success
- **Notes**: No dependencies other than service startup.

### TC-MOCK-002

- **Endpoint Tested**: `/api/customers?page=1&limit=5`
- **Method**: `GET`
- **Description**: Verify pagination returns first page of mock customer list.
- **Request**:
  ```bash
  curl -X GET "http://localhost:5000/api/customers?page=1&limit=5"
  ```
- **Expected Response**:
  - Status: `200 OK`
  - Body shape:
    ```json
    {
        "data": [
            {
                "account_balance": 1432.55,
                "address": "101 Maple St, Austin, TX",
                "created_at": "2024-01-10T09:15:00",
                "customer_id": "CUST-001",
                "date_of_birth": "1990-01-14",
                "email": "avassa.turner@example.com",
                "first_name": "Avassa",
                "last_name": "Turner",
                "phone": "+1-202-555-0101"
            },
            {
                "account_balance": 285.12,
                "address": "22 River Rd, Denver, CO",
                "created_at": "2024-01-11T10:00:00",
                "customer_id": "CUST-002",
                "date_of_birth": "1988-07-20",
                "email": "lisa.brooks@example.com",
                "first_name": "Lisa",
                "last_name": "Brooks",
                "phone": "+1-202-555-0102"
            },
            {
                "account_balance": 9080.44,
                "address": "7 Pine Ave, Seattle, WA",
                "created_at": "2024-01-12T12:05:00",
                "customer_id": "CUST-003",
                "date_of_birth": "1994-05-03",
                "email": "mia.foster@example.com",
                "first_name": "Mia",
                "last_name": "Foster",
                "phone": "+1-202-555-0103"
            },
            {
                "account_balance": 75.0,
                "address": "81 Oak Ln, Miami, FL",
                "created_at": "2024-01-12T14:22:00",
                "customer_id": "CUST-004",
                "date_of_birth": "1985-02-11",
                "email": "noah.hayes@example.com",
                "first_name": "Noah",
                "last_name": "Hayes",
                "phone": "+1-202-555-0104"
            },
            {
                "account_balance": 652.3,
                "address": "350 Cedar St, Boston, MA",
                "created_at": "2024-01-13T08:50:00",
                "customer_id": "CUST-005",
                "date_of_birth": "1991-11-19",
                "email": "emma.reed@example.com",
                "first_name": "Emma",
                "last_name": "Reed",
                "phone": "+1-202-555-0105"
            }
        ],
        "limit": 5,
        "page": 1,
        "total": 24
    }
    ```
- **Progress**: Success
- **Notes**: `data` length should be `<= 5`.

### TC-MOCK-003

- **Endpoint Tested**: `/api/customers?page=999&limit=5`
- **Method**: `GET`
- **Description**: Verify high page number returns empty data array.
- **Request**:
  ```bash
  curl -X GET "http://localhost:5000/api/customers?page=999&limit=5"
  ```
- **Expected Response**:
  - Status: `200 OK`
  - Body:
    ```json
    {
      "data": [],
      "limit": 5,
      "page": 999,
      "total": 24
    }
    ```
- **Progress**: Success
- **Notes**: Endpoint does not treat out-of-range page as error.

### TC-MOCK-004

- **Endpoint Tested**: `/api/customers/CUST-001`
- **Method**: `GET`
- **Description**: Verify retrieval of existing customer from JSON dataset.
- **Request**:
  ```bash
  curl -X GET http://localhost:5000/api/customers/CUST-001
  ```
- **Expected Response**:
  - Status: `200 OK`
  - Body:
  ```json
    {
        "account_balance": 1432.55,
        "address": "101 Maple St, Austin, TX",
        "created_at": "2024-01-10T09:15:00",
        "customer_id": "CUST-001",
        "date_of_birth": "1990-01-14",
        "email": "avassa.turner@example.com",
        "first_name": "Avassa",
        "last_name": "Turner",
        "phone": "+1-202-555-0101"
    }
  ```
- **Progress**: Success
- **Notes**: Field names must match requirement exactly.

### TC-MOCK-005

- **Endpoint Tested**: `/api/customers/CUST-999`
- **Method**: `GET`
- **Description**: Verify missing customer returns 404.
- **Request**:
  ```bash
  curl -X GET http://localhost:5000/api/customers/CUST-999
  ```
- **Expected Response**:
  - Status: `404 Not Found`
  - Body:
    ```json
    {
        "error": "Customer not found"
    }
    ```
- **Progress**: Success
- **Notes**: Confirms requirement for missing customer handling.

### TC-PIPE-001

- **Endpoint Tested**: `/api/health`
- **Method**: `GET`
- **Description**: Verify FastAPI service health endpoint is reachable.
- **Request**:
  ```bash
  curl -X GET http://localhost:8000/api/health
  ```
- **Expected Response**:
  - Status: `200 OK`
  - Body:
    ```json
    {"status":"ok"}
    ```
- **Progress**: Success
- **Notes**: Service must be running and app startup should complete.

### TC-PIPE-002

- **Endpoint Tested**: `/api/ingest`
- **Method**: `POST`
- **Description**: Verify ingestion from mock server and upsert to PostgreSQL.
- **Request**:
  ```bash
  curl -X POST http://localhost:8000/api/ingest
  ```
- **Expected Response**:
  - Status: `200 OK`
  - Body:
    ```json
    {"status":"success","records_processed":24}
    ```
- **Progress**: Success
- **Notes**: If dataset size changes, update expected `records_processed` accordingly.

### TC-PIPE-003

- **Endpoint Tested**: `/api/customers?page=1&limit=5`
- **Method**: `GET`
- **Description**: Verify paginated DB read after ingestion.
- **Request**:
  ```bash
  curl -X GET "http://localhost:8000/api/customers?page=1&limit=5"
  ```
- **Expected Response**:
  - Status: `200 OK`
  - Body shape:
    ```json
    {
        "data": [
            {
                "customer_id": "CUST-001",
                "first_name": "Avassa",
                "last_name": "Turner",
                "email": "avassa.turner@example.com",
                "phone": "+1-202-555-0101",
                "address": "101 Maple St, Austin, TX",
                "date_of_birth": "1990-01-14",
                "account_balance": 1432.55,
                "created_at": "2024-01-10T09:15:00"
            },
            {
                "customer_id": "CUST-002",
                "first_name": "Lisa",
                "last_name": "Brooks",
                "email": "lisa.brooks@example.com",
                "phone": "+1-202-555-0102",
                "address": "22 River Rd, Denver, CO",
                "date_of_birth": "1988-07-20",
                "account_balance": 285.12,
                "created_at": "2024-01-11T10:00:00"
            },
            {
                "customer_id": "CUST-003",
                "first_name": "Mia",
                "last_name": "Foster",
                "email": "mia.foster@example.com",
                "phone": "+1-202-555-0103",
                "address": "7 Pine Ave, Seattle, WA",
                "date_of_birth": "1994-05-03",
                "account_balance": 9080.44,
                "created_at": "2024-01-12T12:05:00"
            },
            {
                "customer_id": "CUST-004",
                "first_name": "Noah",
                "last_name": "Hayes",
                "email": "noah.hayes@example.com",
                "phone": "+1-202-555-0104",
                "address": "81 Oak Ln, Miami, FL",
                "date_of_birth": "1985-02-11",
                "account_balance": 75.0,
                "created_at": "2024-01-12T14:22:00"
            },
            {
                "customer_id": "CUST-005",
                "first_name": "Emma",
                "last_name": "Reed",
                "email": "emma.reed@example.com",
                "phone": "+1-202-555-0105",
                "address": "350 Cedar St, Boston, MA",
                "date_of_birth": "1991-11-19",
                "account_balance": 652.3,
                "created_at": "2024-01-13T08:50:00"
            }
        ],
        "total": 24,
        "page": 1,
        "limit": 5
    }
    ```
- **Progress**: Success
- **Notes**: Run TC-PIPE-002 before this test.

### TC-PIPE-004

- **Endpoint Tested**: `/api/customers/CUST-001`
- **Method**: `GET`
- **Description**: Verify existing customer can be fetched from DB.
- **Request**:
  ```bash
  curl -X GET http://localhost:8000/api/customers/CUST-001
  ```
- **Expected Response**:
  - Status: `200 OK`
  - Body:
    ```json
    {
      "customer_id": "CUST-001",
      "first_name": "Avassa",
      "last_name": "Turner",
      "email": "avassa.turner@example.com",
      "phone": "+1-202-555-0101",
      "address": "101 Maple St, Austin, TX",
      "date_of_birth": "1990-01-14",
      "account_balance": 1432.55,
      "created_at": "2024-01-10T09:15:00"
    }
    ```
- **Progress**: Success
- **Notes**: Validates lookup endpoint against persisted data.

### TC-PIPE-005

- **Endpoint Tested**: `/api/customers/CUST-999`
- **Method**: `GET`
- **Description**: Verify missing customer returns 404 from DB-backed API.
- **Request**:
  ```bash
  curl -X GET http://localhost:8000/api/customers/CUST-999
  ```
- **Expected Response**:
  - Status: `404 Not Found`
  - Body:
    ```json
    {
      "detail": "Customer not found"
    }
    ```
- **Progress**: Success
- **Notes**: Confirms missing record handling.

### TC-PIPE-006

- **Endpoint Tested**: `/api/customers?page=0&limit=5`
- **Method**: `GET`
- **Description**: Verify query validation rejects invalid page number.
- **Request**:
  ```bash
  curl -X GET "http://localhost:8000/api/customers?page=0&limit=5"
  ```
- **Expected Response**:
  - Status: `422 Unprocessable Entity`
  - Body includes validation error for `page`.
- **Progress**: Success
- **Notes**: FastAPI query constraint is `page >= 1`.

### TC-PIPE-007

- **Endpoint Tested**: `/api/customers?page=1&limit=101`
- **Method**: `GET`
- **Description**: Verify query validation rejects invalid page size.
- **Request**:
  ```bash
  curl -X GET "http://localhost:8000/api/customers?page=1&limit=101"
  ```
- **Expected Response**:
  - Status: `422 Unprocessable Entity`
  - Body includes validation error for `limit`.
- **Progress**: Success
- **Notes**: FastAPI query constraint is `limit <= 100`.
