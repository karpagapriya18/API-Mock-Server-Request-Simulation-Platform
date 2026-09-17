from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/docs-examples", tags=["swagger guide"])


class SwaggerStep(BaseModel):
    step: int = Field(..., examples=[1])
    action: str = Field(..., examples=["Register a user"])
    endpoint: str = Field(..., examples=["POST /api/auth/register"])
    notes: str = Field(..., examples=["Copy the access_token from the response."])


class SwaggerTestingFlow(BaseModel):
    title: str
    steps: list[SwaggerStep]

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Complete Swagger testing flow",
                "steps": [
                    {
                        "step": 1,
                        "action": "Register",
                        "endpoint": "POST /api/auth/register",
                        "notes": "Create a user and copy the returned access_token.",
                    },
                    {
                        "step": 2,
                        "action": "Authorize Swagger",
                        "endpoint": "Authorize button",
                        "notes": "Paste Bearer <access_token>.",
                    },
                    {
                        "step": 3,
                        "action": "Create mock API",
                        "endpoint": "POST /api/mock-apis",
                        "notes": "Use the sample mock API payload.",
                    },
                    {
                        "step": 4,
                        "action": "Execute mock API",
                        "endpoint": "GET /mock/users/123",
                        "notes": "Use scenario=not-found to test a configured error response.",
                    },
                ],
            }
        }
    }


class ExamplePayload(BaseModel):
    name: str
    payload: dict


@router.get(
    "/testing-flow",
    response_model=SwaggerTestingFlow,
    summary="Swagger testing flow",
    description="A step-by-step guide for testing the platform directly from Swagger UI.",
)
def testing_flow():
    return {
        "title": "Complete Swagger testing flow",
        "steps": [
            {
                "step": 1,
                "action": "Register or log in",
                "endpoint": "POST /api/auth/register or POST /api/auth/login",
                "notes": "Copy the access_token from the response.",
            },
            {
                "step": 2,
                "action": "Authorize Swagger",
                "endpoint": "Authorize button",
                "notes": "Paste Bearer <access_token> into the value field.",
            },
            {
                "step": 3,
                "action": "Create a mock API",
                "endpoint": "POST /api/mock-apis",
                "notes": "Use the sample payload from /api/docs-examples/mock-api-payload.",
            },
            {
                "step": 4,
                "action": "Execute the dynamic mock endpoint",
                "endpoint": "GET /mock/users/123",
                "notes": "Try ?scenario=not-found or header X-Mock-Scenario: not-found.",
            },
            {
                "step": 5,
                "action": "Check monitoring",
                "endpoint": "GET /api/dashboard/summary and GET /api/request-logs",
                "notes": "These endpoints show request count, errors, usage, and response time.",
            },
        ],
    }


@router.get(
    "/mock-api-payload",
    response_model=ExamplePayload,
    summary="Copy-paste mock API creation payload",
    description="A complete example body for POST /api/mock-apis with success, not-found, unauthorized, and server-error scenarios.",
)
def mock_api_payload():
    return {
        "name": "Create mock users endpoint",
        "payload": {
            "name": "Get user by ID",
            "method": "GET",
            "path": "/users/{id}",
            "visibility": "public",
            "auth_mode": "none",
            "is_active": True,
            "versions": [
                {
                    "version": "v1",
                    "is_default": True,
                    "response_delay_ms": 150,
                    "request_schema": {
                        "query_schema": {
                            "type": "object",
                            "properties": {
                                "include": {"type": "string", "enum": ["profile", "roles", "all"]}
                            },
                            "additionalProperties": True,
                        },
                        "headers_schema": {
                            "type": "object",
                            "properties": {
                                "x-client-id": {"type": "string"}
                            },
                            "additionalProperties": True,
                        },
                        "body_schema": None,
                    },
                    "response_templates": [
                        {
                            "scenario": "success",
                            "status_code": 200,
                            "headers": {"x-mock-scenario": "success"},
                            "body": {"id": 123, "name": "Ada Lovelace", "role": "admin"},
                            "is_default": True,
                        },
                        {
                            "scenario": "not-found",
                            "status_code": 404,
                            "headers": {"x-mock-scenario": "not-found"},
                            "body": {"error": "User not found", "code": "USER_NOT_FOUND"},
                            "is_default": False,
                        },
                        {
                            "scenario": "unauthorized",
                            "status_code": 401,
                            "headers": {"x-mock-scenario": "unauthorized"},
                            "body": {"error": "Missing or invalid token"},
                            "is_default": False,
                        },
                        {
                            "scenario": "server-error",
                            "status_code": 500,
                            "headers": {"x-mock-scenario": "server-error"},
                            "body": {"error": "Simulated upstream failure"},
                            "is_default": False,
                        },
                    ],
                }
            ],
        },
    }


@router.get(
    "/curl-commands",
    summary="Useful curl commands",
    description="Copy these command shapes when testing outside Swagger or in Postman.",
)
def curl_commands():
    return {
        "register": "curl -X POST http://127.0.0.1:8000/api/auth/register -H \"Content-Type: application/json\" -d \"{\\\"email\\\":\\\"dev@example.com\\\",\\\"password\\\":\\\"secret123\\\",\\\"name\\\":\\\"Developer\\\"}\"",
        "create_mock_api": "curl -X POST http://127.0.0.1:8000/api/mock-apis -H \"Authorization: Bearer <token>\" -H \"Content-Type: application/json\" -d @mock-api.json",
        "execute_success": "curl http://127.0.0.1:8000/mock/users/123",
        "execute_not_found": "curl \"http://127.0.0.1:8000/mock/users/123?scenario=not-found\"",
        "dashboard": "curl http://127.0.0.1:8000/api/dashboard/summary -H \"Authorization: Bearer <token>\"",
    }
