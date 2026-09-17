from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import MockApi, RequestLog, User
from app.schemas.mock_api import RequestLogOut

router = APIRouter(prefix="/request-logs", tags=["Traffic"])


@router.get(
    "",
    response_model=list[RequestLogOut],
    summary="List traffic",
    description="",
    responses={401: {"description": "Missing or invalid bearer token"}},
)
def list_request_logs(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    endpoint: str | None = Query(default=None, description="Filter logs by endpoint text."),
    status_min: int | None = Query(default=None, description="Filter logs with response status greater than or equal to this value."),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of logs to return."),
    offset: int = Query(0, ge=0, description="Number of logs to skip."),
):
    api_ids = [row.id for row in db.query(MockApi.id).filter(MockApi.owner_id == user.id).all()]
    query = db.query(RequestLog).filter(RequestLog.api_id.in_(api_ids))
    if endpoint:
        query = query.filter(RequestLog.endpoint.contains(endpoint))
    if status_min:
        query = query.filter(RequestLog.response_status >= status_min)
    return query.order_by(RequestLog.timestamp.desc()).offset(offset).limit(limit).all()
