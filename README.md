# API Mock Server & Request Simulation Platform

A full-stack mock API studio for defining endpoints, validating requests, simulating responses, and tracking request history.

## Stack

- Backend: Python 3.12, FastAPI, SQLAlchemy, Alembic, Pydantic, Redis, JWT
- Frontend: React, Vite, TypeScript, Material UI, Axios, React Router
- Database: MySQL 8.0
- Tooling: Docker Compose, Swagger/OpenAPI, Postman, Pytest

## Run with Docker

```bash
cp .env.example .env
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- Swagger/OpenAPI: http://localhost:8000/docs
- MySQL: localhost:3306
- Redis: localhost:6379

## Dynamic Mock Execution

Create a mock definition through the UI or `POST /api/mock-apis`, then call it at:

```text
GET /mock/users
POST /mock/orders
GET /mock/products/123
```

Templated paths such as `/products/{id}` are matched dynamically. Scenarios can be selected with either:

```text
?scenario=not-found
X-Mock-Scenario: server-error
```

API versions can be selected with either:

```text
?version=v2
X-API-Version: v2
```

## Request Validation

Definitions support JSON Schema validation for:

- Query parameters
- Headers
- Request body

Validation failures return HTTP `422` with the failing location and message.

## Authentication and Access

- Users register and log in with JWT bearer tokens.
- Mock definitions are managed under `/api/mock-apis`.
- Private APIs require the owner or an explicit `api_permissions` grant.
- Endpoint-level auth can be set with `auth_mode: "bearer"`.

## Request History and Dashboard

Every invocation stores endpoint, method, params, headers, request body, response status, response time, and timestamp in `request_logs`.

Dashboard metrics include total APIs, active APIs, total requests, error requests, most used endpoints, and average response time.

## Local Backend Commands

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
pytest
```

## Local Frontend Commands

```bash
cd frontend
npm install
npm run dev
```

## Postman

Import `postman/mock-api-platform.postman_collection.json`. After login, copy the returned token into the collection `token` variable.

## Important Files

- `backend/app/main.py`: FastAPI app and router registration
- `backend/app/models/entities.py`: SQLAlchemy tables
- `backend/app/services/mock_executor.py`: dynamic endpoint matching, validation, responses, logging
- `backend/alembic/versions/0001_initial.py`: initial migration
- `frontend/src/pages/MockApis.tsx`: API definition and request simulation UI
