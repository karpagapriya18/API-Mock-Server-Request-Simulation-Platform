from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import ApiVersion, MockApi, RequestSchema, ResponseTemplate, User
from app.schemas.mock_api import MockApiCreate, MockApiOut, MockApiUpdate
from app.services.cache import cache_delete
from app.services.mock_executor import owned_or_permitted_query

router = APIRouter(prefix="/mock-apis", tags=["Mock Builder"])


@router.post(
    "",
    response_model=MockApiOut,
    status_code=201,
    summary="Create mock",
    description="",
    responses={
        201: {"description": "Mock API created"},
        401: {"description": "Missing or invalid bearer token"},
        422: {"description": "Invalid request definition"},
    },
)
def create_mock_api(payload: MockApiCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    api = MockApi(
        owner_id=user.id,
        name=payload.name,
        method=payload.method,
        path=payload.path,
        visibility=payload.visibility,
        auth_mode=payload.auth_mode,
        is_active=payload.is_active,
    )
    for item in payload.versions:
        version = ApiVersion(version=item.version, is_default=item.is_default, response_delay_ms=item.response_delay_ms)
        version.request_schema = RequestSchema(**item.request_schema.model_dump())
        version.response_templates = [ResponseTemplate(**template.model_dump()) for template in item.response_templates]
        api.versions.append(version)
    db.add(api)
    db.commit()
    db.refresh(api)
    cache_delete("mock:*")
    return api


@router.get(
    "",
    response_model=list[MockApiOut],
    summary="List mocks",
    description="",
    responses={401: {"description": "Missing or invalid bearer token"}},
)
def list_mock_apis(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    method: str | None = Query(default=None, description="Filter by HTTP method, for example GET or POST."),
    active: bool | None = Query(default=None, description="Filter active or inactive APIs."),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of APIs to return."),
    offset: int = Query(0, ge=0, description="Number of APIs to skip."),
):
    query = owned_or_permitted_query(db, user)
    if method:
        query = query.filter(MockApi.method == method.upper())
    if active is not None:
        query = query.filter(MockApi.is_active.is_(active))
    return query.order_by(MockApi.created_at.desc()).offset(offset).limit(limit).all()


@router.patch(
    "/{api_id}",
    response_model=MockApiOut,
    summary="Update mock",
    description="",
    responses={
        200: {"description": "Mock API updated"},
        401: {"description": "Missing or invalid bearer token"},
        404: {"description": "Mock API not found or not owned by current user"},
    },
)
def update_mock_api(
    api_id: Annotated[int, Path(description="Mock API ID.")],
    payload: MockApiUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    api = db.query(MockApi).filter(MockApi.id == api_id, MockApi.owner_id == user.id).first()
    if not api:
        raise HTTPException(status_code=404, detail="Mock API not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(api, key, value)
    db.commit()
    db.refresh(api)
    cache_delete("mock:*")
    return api


@router.delete(
    "/{api_id}",
    status_code=204,
    summary="Delete mock",
    description="",
    responses={
        204: {"description": "Mock API deleted"},
        401: {"description": "Missing or invalid bearer token"},
        404: {"description": "Mock API not found or not owned by current user"},
    },
)
def delete_mock_api(
    api_id: Annotated[int, Path(description="Mock API ID.")],
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    api = db.query(MockApi).filter(MockApi.id == api_id, MockApi.owner_id == user.id).first()
    if not api:
        raise HTTPException(status_code=404, detail="Mock API not found")
    db.delete(api)
    db.commit()
    cache_delete("mock:*")
    return None
