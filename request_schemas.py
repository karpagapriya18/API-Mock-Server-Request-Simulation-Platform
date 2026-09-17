from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import ApiVersion, MockApi, RequestSchema, User
from app.schemas.mock_api import RequestSchemaIn, RequestSchemaOut
from app.services.cache import cache_delete

router = APIRouter(prefix="/mock-apis/{mock_api_id}/versions/{version_id}/request-schema", tags=["Validation Rules"])


def _owner_version(db: Session, mock_api_id: int, version_id: int, user: User) -> ApiVersion:
    version = (
        db.query(ApiVersion)
        .join(MockApi)
        .filter(ApiVersion.id == version_id, ApiVersion.api_id == mock_api_id, MockApi.owner_id == user.id)
        .first()
    )
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return version


@router.post("", response_model=RequestSchemaOut, status_code=201, summary="Create validation rule")
def create_request_schema(
    mock_api_id: Annotated[int, Path(description="Mock API ID")],
    version_id: Annotated[int, Path(description="Version ID")],
    payload: RequestSchemaIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _owner_version(db, mock_api_id, version_id, user)
    existing = db.query(RequestSchema).filter(RequestSchema.version_id == version_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Request schema already exists for this version")
    schema = RequestSchema(version_id=version_id, **payload.model_dump())
    db.add(schema)
    db.commit()
    db.refresh(schema)
    cache_delete("mock:*")
    return schema


@router.get("", response_model=RequestSchemaOut, summary="Get validation rule")
def get_request_schema(
    mock_api_id: Annotated[int, Path(description="Mock API ID")],
    version_id: Annotated[int, Path(description="Version ID")],
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _owner_version(db, mock_api_id, version_id, user)
    schema = db.query(RequestSchema).filter(RequestSchema.version_id == version_id).first()
    if not schema:
        raise HTTPException(status_code=404, detail="Request schema not found")
    return schema


@router.put("", response_model=RequestSchemaOut, summary="Update validation rule")
def update_request_schema(
    mock_api_id: Annotated[int, Path(description="Mock API ID")],
    version_id: Annotated[int, Path(description="Version ID")],
    payload: RequestSchemaIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _owner_version(db, mock_api_id, version_id, user)
    schema = db.query(RequestSchema).filter(RequestSchema.version_id == version_id).first()
    if not schema:
        schema = RequestSchema(version_id=version_id)
        db.add(schema)
    for key, value in payload.model_dump().items():
        setattr(schema, key, value)
    db.commit()
    db.refresh(schema)
    cache_delete("mock:*")
    return schema


@router.delete("", status_code=204, summary="Delete validation rule")
def delete_request_schema(
    mock_api_id: Annotated[int, Path(description="Mock API ID")],
    version_id: Annotated[int, Path(description="Version ID")],
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _owner_version(db, mock_api_id, version_id, user)
    schema = db.query(RequestSchema).filter(RequestSchema.version_id == version_id).first()
    if not schema:
        raise HTTPException(status_code=404, detail="Request schema not found")
    db.delete(schema)
    db.commit()
    cache_delete("mock:*")
    return None
