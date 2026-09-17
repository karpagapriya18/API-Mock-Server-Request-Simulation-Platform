from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    api_versions,
    auth,
    dashboard,
    logs,
    mock_apis,
    mock_runtime,
    permissions,
    request_schemas,
    response_scenarios,
)
from app.core.config import get_settings

settings = get_settings()
description = "Design mock endpoints, run them instantly, and review traffic."

tags_metadata = [
    {"name": "Access", "description": "User sessions and current account."},
    {"name": "Mock Builder", "description": "Main mock endpoint records."},
    {"name": "Revisions", "description": "Version sets for a mock."},
    {"name": "Validation Rules", "description": "Input checks for a version."},
    {"name": "Reply Templates", "description": "Scenario-based mock replies."},
    {"name": "Sharing", "description": "Private mock access rules."},
    {"name": "Analytics", "description": "Usage totals and timing."},
    {"name": "Traffic", "description": "Captured calls."},
    {"name": "Live Runner", "description": "Runtime mock URLs."},
    {"name": "System", "description": "Service status."},
]

app = FastAPI(
    title="API MOCK SERVER",
    summary="Mock API workspace backend.",
    description=description,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={"name": "Mock API Platform Team"},
    license_info={"name": "MIT"},
    openapi_tags=tags_metadata,
    swagger_ui_parameters={
        "defaultModelsExpandDepth": 2,
        "defaultModelExpandDepth": 3,
        "displayRequestDuration": True,
        "filter": False,
        "persistAuthorization": True,
        "tryItOutEnabled": True,
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(mock_apis.router, prefix="/api")
app.include_router(api_versions.router, prefix="/api")
app.include_router(request_schemas.router, prefix="/api")
app.include_router(response_scenarios.router, prefix="/api")
app.include_router(permissions.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(logs.router, prefix="/api")
app.include_router(mock_runtime.router)


@app.get("/", tags=["System"], summary="Root")
def root():
    return {"name": settings.app_name, "docs": "/docs", "health": "/health"}


@app.get(
    "/health",
    tags=["System"],
    summary="Health check",
    description="",
    responses={200: {"description": "Backend is healthy", "content": {"application/json": {"example": {"status": "ok"}}}}},
)
def health():
    return {"status": "ok"}
