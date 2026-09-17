from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import MockApi, RequestLog, User
from app.services.cache import cache_get, cache_set

router = APIRouter(prefix="/dashboard", tags=["Analytics"])


@router.get(
    "/summary",
    summary="Get metrics",
    description="",
    responses={
        200: {
            "description": "Dashboard metrics",
            "content": {
                "application/json": {
                    "example": {
                        "total_mock_apis": 5,
                        "active_apis": 4,
                        "total_requests": 120,
                        "error_requests": 9,
                        "average_response_time_ms": 87.45,
                        "most_used_endpoints": [{"endpoint": "/users/123", "count": 42}],
                    }
                }
            },
        },
        401: {"description": "Missing or invalid bearer token"},
    },
)
def dashboard_summary(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cache_key = f"dashboard:{user.id}"
    cached = cache_get(cache_key)
    if cached:
        return cached
    api_ids = [row.id for row in db.query(MockApi.id).filter(MockApi.owner_id == user.id).all()]
    total_mock_apis = len(api_ids)
    active_apis = db.query(func.count(MockApi.id)).filter(MockApi.owner_id == user.id, MockApi.is_active.is_(True)).scalar()
    logs = db.query(RequestLog).filter(RequestLog.api_id.in_(api_ids)) if api_ids else db.query(RequestLog).filter(False)
    most_used = (
        db.query(RequestLog.endpoint, func.count(RequestLog.id).label("count"))
        .filter(RequestLog.api_id.in_(api_ids))
        .group_by(RequestLog.endpoint)
        .order_by(func.count(RequestLog.id).desc())
        .limit(5)
        .all()
        if api_ids
        else []
    )
    result = {
        "total_mock_apis": total_mock_apis,
        "active_apis": active_apis or 0,
        "total_requests": logs.count(),
        "error_requests": logs.filter(RequestLog.response_status >= 400).count(),
        "average_response_time_ms": round(float(logs.with_entities(func.avg(RequestLog.response_time_ms)).scalar() or 0), 2),
        "most_used_endpoints": [{"endpoint": endpoint, "count": count} for endpoint, count in most_used],
    }
    cache_set(cache_key, result, ttl_seconds=15)
    return result
