from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.model_config import (
    ModelConfigCreate,
    ModelConfigResponse,
    ModelConfigUpdate
)
from app.services.model_config import create_model_config , list_model_configs , get_model_config , update_model_config , delete_model_config

from app.api.deps import get_db, get_current_user


router = APIRouter(tags=["Model Configurations"])


@router.post(
    "/projects/{project_id}/models",
    response_model=ModelConfigResponse,
    status_code=status.HTTP_201_CREATED
)
def create_model_config_endpoint(
    project_id: int,
    payload: ModelConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_model_config(
        db=db,
        project_id=project_id,
        current_user=current_user,
        payload=payload
    )

@router.get(
    "/projects/{project_id}/models",
    response_model=list[ModelConfigResponse]
)
def get_model_configs(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return list_model_configs(
        db=db,
        project_id=project_id,
        current_user=current_user
    )


@router.patch(
    "/models/{model_id}",
    response_model=ModelConfigResponse
)
def update_model_config_endpoint(
    model_id: int,
    payload: ModelConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_model_config(
        db=db,
        model_id=model_id,
        current_user=current_user,
        payload=payload
    )

@router.delete(
    "/models/{model_id}",
    status_code=status.HTTP_200_OK
)
def delete_model_config_endpoint(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return delete_model_config(
        db=db,
        model_id=model_id,
        current_user=current_user
    )