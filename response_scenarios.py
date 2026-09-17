from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import ApiVersion, MockApi, ResponseTemplate, User
from app.schemas.mock_api import ResponseTemplateCreate, ResponseTemplateOut, ResponseTemplateUpdate
from app.services.cache import cache_delete

router = APIRouter(prefix="/mock-apis/{mock_api_id}/versions/{version_id}/responses", tags=["Reply Templates"])


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


@router.post("", response_model=ResponseTemplateOut, status_code=201, summary="Create reply template")
def create_response(
    mock_api_id: Annotated[int, Path(description="Mock API ID")],
    version_id: Annotated[int, Path(description="Version ID")],
    payload: ResponseTemplateCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _owner_version(db, mock_api_id, version_id, user)
    if payload.is_default:
        db.query(ResponseTemplate).filter(ResponseTemplate.version_id == version_id).update({"is_default": False})
    response = ResponseTemplate(version_id=version_id, **payload.model_dump())
    db.add(response)
    db.commit()
    db.refresh(response)
    cache_delete("mock:*")
    return response


@router.get("", response_model=list[ResponseTemplateOut], summary="List reply templates")
def list_responses(
    mock_api_id: Annotated[int, Path(description="Mock API ID")],
    version_id: Annotated[int, Path(description="Version ID")],
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _owner_version(db, mock_api_id, version_id, user)
    return db.query(ResponseTemplate).filter(ResponseTemplate.version_id == version_id).order_by(ResponseTemplate.id.desc()).all()


@router.get("/{response_id}", response_model=ResponseTemplateOut, summary="Get reply template")
def get_response(
    mock_api_id: Annotated[int, Path(description="Mock API ID")],
    version_id: Annotated[int, Path(description="Version ID")],
    response_id: Annotated[int, Path(description="Response scenario ID")],
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _owner_version(db, mock_api_id, version_id, user)
    response = db.query(ResponseTemplate).filter(ResponseTemplate.id == response_id, ResponseTemplate.version_id == version_id).first()
    if not response:
        raise HTTPException(status_code=404, detail="Response scenario not found")
    return response


@router.put("/{response_id}", response_model=ResponseTemplateOut, summary="Update reply template")
def update_response(
    mock_api_id: Annotated[int, Path(description="Mock API ID")],
    version_id: Annotated[int, Path(description="Version ID")],
    response_id: Annotated[int, Path(description="Response scenario ID")],
    payload: ResponseTemplateUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _owner_version(db, mock_api_id, version_id, user)
    response = db.query(ResponseTemplate).filter(ResponseTemplate.id == response_id, ResponseTemplate.version_id == version_id).first()
    if not response:
        raise HTTPException(status_code=404, detail="Response scenario not found")
    if payload.is_default:
        db.query(ResponseTemplate).filter(ResponseTemplate.version_id == version_id).update({"is_default": False})
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(response, key, value)
    db.commit()
    db.refresh(response)
    cache_delete("mock:*")
    return response


@router.delete("/{response_id}", status_code=204, summary="Delete reply template")
def delete_response(
    mock_api_id: Annotated[int, Path(description="Mock API ID")],
    version_id: Annotated[int, Path(description="Version ID")],
    response_id: Annotated[int, Path(description="Response scenario ID")],
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _owner_version(db, mock_api_id, version_id, user)
    response = db.query(ResponseTemplate).filter(ResponseTemplate.id == response_id, ResponseTemplate.version_id == version_id).first()
    if not response:
        raise HTTPException(status_code=404, detail="Response scenario not found")
    db.delete(response)
    db.commit()
    cache_delete("mock:*")
    return None
