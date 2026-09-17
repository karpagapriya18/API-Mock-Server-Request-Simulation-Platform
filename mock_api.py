from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class ResponseTemplateIn(BaseModel):
    scenario: str = Field(default="success", examples=["success", "validation-error", "unauthorized", "not-found", "server-error"])
    status_code: int = Field(default=200, ge=100, le=599, examples=[200])
    headers: dict[str, str] | None = Field(default=None, examples=[{"x-powered-by": "mock-api-platform"}])
    body: Any = Field(default=None, examples=[{"id": 123, "name": "Ada Lovelace"}])
    is_default: bool = Field(default=True, description="Used when no scenario is requested.")


class RequestSchemaIn(BaseModel):
    query_schema: dict[str, Any] | None = Field(
        default=None,
        description="JSON Schema used to validate query parameters.",
        examples=[{"type": "object", "properties": {"page": {"type": "string"}}}],
    )
    headers_schema: dict[str, Any] | None = Field(
        default=None,
        description="JSON Schema used to validate request headers. Header names are lowercased.",
        examples=[{"type": "object", "properties": {"x-client-id": {"type": "string"}}}],
    )
    body_schema: dict[str, Any] | None = Field(
        default=None,
        description="JSON Schema used to validate JSON request bodies.",
        examples=[{"type": "object", "required": ["name"], "properties": {"name": {"type": "string"}}}],
    )


class ApiVersionIn(BaseModel):
    version: str = Field(default="v1", examples=["v1"])
    is_default: bool = Field(default=True, description="Default version when no version header/query parameter is sent.")
    response_delay_ms: int = Field(default=0, ge=0, le=60000, description="Artificial response delay in milliseconds.")
    request_schema: RequestSchemaIn = Field(default_factory=RequestSchemaIn)
    response_templates: list[ResponseTemplateIn] = Field(default_factory=lambda: [ResponseTemplateIn()])


class ApiVersionCreate(BaseModel):
    version: str = Field(default="v2", examples=["v2"])
    is_default: bool = False
    response_delay_ms: int = Field(default=0, ge=0, le=60000)


class ApiVersionUpdate(BaseModel):
    version: str | None = Field(default=None, examples=["v2"])
    is_default: bool | None = None
    response_delay_ms: int | None = Field(default=None, ge=0, le=60000)


class ApiVersionOut(BaseModel):
    id: int
    api_id: int
    version: str
    is_default: bool
    response_delay_ms: int
    created_at: datetime

    model_config = {"from_attributes": True}


class RequestSchemaOut(BaseModel):
    id: int
    version_id: int
    query_schema: dict[str, Any] | None
    headers_schema: dict[str, Any] | None
    body_schema: dict[str, Any] | None

    model_config = {"from_attributes": True}


class ResponseTemplateCreate(ResponseTemplateIn):
    pass


class ResponseTemplateUpdate(BaseModel):
    scenario: str | None = Field(default=None, examples=["custom-error"])
    status_code: int | None = Field(default=None, ge=100, le=599)
    headers: dict[str, str] | None = None
    body: Any = None
    is_default: bool | None = None


class ResponseTemplateOut(BaseModel):
    id: int
    version_id: int
    scenario: str
    status_code: int
    headers: dict[str, str] | None
    body: Any
    is_default: bool

    model_config = {"from_attributes": True}


class ApiPermissionCreate(BaseModel):
    user_id: int = Field(..., examples=[2])
    can_invoke: bool = True


class ApiPermissionOut(BaseModel):
    id: int
    api_id: int
    user_id: int
    can_invoke: bool

    model_config = {"from_attributes": True}


class MockApiCreate(BaseModel):
    name: str = Field(..., examples=["Get user by ID"])
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"] = Field(..., examples=["GET"])
    path: str = Field(..., pattern=r"^/[A-Za-z0-9_/{}/.-]*$", examples=["/users/{id}"])
    visibility: Literal["public", "private"] = Field(default="private", description="Private APIs require owner or permission access.")
    auth_mode: Literal["none", "bearer"] = Field(default="none", description="Endpoint-level authentication mode for execution.")
    is_active: bool = Field(default=True)
    versions: list[ApiVersionIn] = Field(default_factory=lambda: [ApiVersionIn()])

    model_config = {
        "json_schema_extra": {
            "example": {
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
                        "response_delay_ms": 100,
                        "request_schema": {
                            "query_schema": {
                                "type": "object",
                                "properties": {
                                    "include": {"type": "string"}
                                },
                            },
                            "headers_schema": None,
                            "body_schema": None,
                        },
                        "response_templates": [
                            {
                                "scenario": "success",
                                "status_code": 200,
                                "headers": {"x-mock-source": "swagger"},
                                "body": {"id": 123, "name": "Ada Lovelace", "role": "admin"},
                                "is_default": True,
                            },
                            {
                                "scenario": "not-found",
                                "status_code": 404,
                                "headers": None,
                                "body": {"error": "User not found"},
                                "is_default": False,
                            },
                        ],
                    }
                ],
            }
        }
    }


class MockApiUpdate(BaseModel):
    name: str | None = Field(default=None, examples=["Updated mock API name"])
    visibility: Literal["public", "private"] | None = None
    auth_mode: Literal["none", "bearer"] | None = None
    is_active: bool | None = None


class MockApiOut(BaseModel):
    id: int
    name: str
    method: str
    path: str
    visibility: str
    auth_mode: str
    is_active: bool
    created_at: datetime

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "Get user by ID",
                "method": "GET",
                "path": "/users/{id}",
                "visibility": "public",
                "auth_mode": "none",
                "is_active": True,
                "created_at": "2026-09-15T15:30:00",
            }
        },
    }


class RequestLogOut(BaseModel):
    id: int
    method: str
    endpoint: str
    response_status: int
    response_time_ms: int
    timestamp: datetime

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 10,
                "method": "GET",
                "endpoint": "/users/123",
                "response_status": 200,
                "response_time_ms": 104,
                "timestamp": "2026-09-15T15:35:00",
            }
        },
    }
