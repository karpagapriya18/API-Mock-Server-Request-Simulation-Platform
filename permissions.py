from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import ApiPermission, MockApi, User
from app.schemas.mock_api import ApiPermissionCreate, ApiPermissionOut
from app.services.cache import cache_delete

router = APIRouter(prefix="/mock-apis/{mock_api_id}/permissions", tags=["Sharing"])


def _owner_api(db: Session, mock_api_id: int, user: User) -> MockApi:
    api = db.query(MockApi).filter(MockApi.id == mock_api_id, MockApi.owner_id == user.id).first()
    if not api:
        raise HTTPException(status_code=404, detail="Mock API not found")
    return api


@router.post("", response_model=ApiPermissionOut, status_code=201, summary="Share mock")
def create_permission(
    mock_api_id: Annotated[int, Path(description="Mock API ID")],
    payload: ApiPermissionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _owner_api(db, mock_api_id, user)
    permission = ApiPermission(api_id=mock_api_id, **payload.model_dump())
    db.add(permission)
    db.commit()
    db.refresh(permission)
    cache_delete("mock:*")
    return permission


@router.get("", response_model=list[ApiPermissionOut], summary="List sharing rules")
def list_permissions(
    mock_api_id: Annotated[int, Path(description="Mock API ID")],
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _owner_api(db, mock_api_id, user)
    return db.query(ApiPermission).filter(ApiPermission.api_id == mock_api_id).order_by(ApiPermission.id.desc()).all()


@router.delete("/{permission_id}", status_code=204, summary="Remove sharing rule")
def delete_permission(
    mock_api_id: Annotated[int, Path(description="Mock API ID")],
    permission_id: Annotated[int, Path(description="Permission ID")],
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _owner_api(db, mock_api_id, user)
    permission = db.query(ApiPermission).filter(ApiPermission.id == permission_id, ApiPermission.api_id == mock_api_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    db.delete(permission)
    db.commit()
    cache_delete("mock:*")
    return None
