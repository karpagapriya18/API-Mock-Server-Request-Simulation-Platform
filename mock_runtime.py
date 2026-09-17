from typing import Annotated

from fastapi import APIRouter, Depends, Path, Request
from sqlalchemy.orm import Session

from app.api.deps import get_optional_user
from app.db.session import get_db
from app.models.entities import User
from app.services.mock_executor import execute_mock

router = APIRouter(prefix="/mock", tags=["Live Runner"])


@router.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
    summary="Run mock",
    description="",
    responses={
        200: {"description": "Configured mock response. Actual status/body can vary by response template."},
        403: {"description": "Private API or bearer-protected mock API is not accessible to this caller."},
        404: {"description": "No active mock API definition matched this method and path."},
        422: {"description": "Incoming request failed the configured JSON Schema validation."},
    },
)
async def execute(
    path: Annotated[str, Path(description="Dynamic path after `/mock`, for example `users/123`.")],
    request: Request,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    return await execute_mock(db, request, user)
