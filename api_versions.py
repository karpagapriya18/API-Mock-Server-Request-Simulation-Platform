from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import ApiVersion, MockApi, RequestSchema, User
from app.schemas.mock_api import ApiVersionCreate, ApiVersionOut, ApiVersionUpdate
from app.services.cache import cache_delete

router = APIRouter(prefix="/mock-apis/{mock_api_id}/versions", tags=["Revisions"])


def _owner_api(db: Session, mock_api_id: int, user: User) -> MockApi:
    api = db.query(MockApi).filter(MockApi.id == mock_api_id, MockApi.owner_id == user.id).first()
    if not api:
        raise HTTPException(status_code=404, detail="Mock API not found")
    return api


@router.post("", response_model=ApiVersionOut, status_code=201, summary="Create revision")
def create_version(
    mock_api_id: Annotated[int, Path(description="Mock API ID")],
    payload: ApiVersionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _owner_api(db, mock_api_id, user)
    if payload.is_default:
        db.query(ApiVersion).filter(ApiVersion.api_id == mock_api_id).update({"is_default": False})
    version = ApiVersion(api_id=mock_api_id, **payload.model_dump())
    version.request_schema = RequestSchema()
    db.add(version)
    db.commit()
    db.refresh(version)
    cache_delete("mock:*")
    return version


@router.get("", response_model=list[ApiVersionOut], summary="List revisions")
def list_versions(
    mock_api_id: Annotated[int, Path(description="Mock API ID")],
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _owner_api(db, mock_api_id, user)
    return db.query(ApiVersion).filter(ApiVersion.api_id == mock_api_id).order_by(ApiVersion.created_at.desc()).all()


@router.get("/{version_id}", response_model=ApiVersionOut, summary="Get revision")
def get_version(
    mock_api_id: Annotated[int, Path(description="Mock API ID")],
    version_id: Annotated[int, Path(description="Version ID")],
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _owner_api(db, mock_api_id, user)
    version = db.query(ApiVersion).filter(ApiVersion.id == version_id, ApiVersion.api_id == mock_api_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return version


@router.put("/{version_id}", response_model=ApiVersionOut, summary="Update revision")
def update_version(
    mock_api_id: Annotated[int, Path(description="Mock API ID")],
    version_id: Annotated[int, Path(description="Version ID")],
    payload: ApiVersionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _owner_api(db, mock_api_id, user)
    version = db.query(ApiVersion).filter(ApiVersion.id == version_id, ApiVersion.api_id == mock_api_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    if payload.is_default:
        db.query(ApiVersion).filter(ApiVersion.api_id == mock_api_id).update({"is_default": False})
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(version, key, value)
    db.commit()
    db.refresh(version)
    cache_delete("mock:*")
    return version


@router.delete("/{version_id}", status_code=204, summary="Delete revision")
def delete_version(
    mock_api_id: Annotated[int, Path(description="Mock API ID")],
    version_id: Annotated[int, Path(description="Version ID")],
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _owner_api(db, mock_api_id, user)
    version = db.query(ApiVersion).filter(ApiVersion.id == version_id, ApiVersion.api_id == mock_api_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    db.delete(version)
    db.commit()
    cache_delete("mock:*")
    return None
