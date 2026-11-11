from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.project import Project
from app.models.model_config import ModelConfig
from app.models.user import User

from app.schemas.model_config import ModelConfigCreate , ModelConfigUpdate



def create_model_config(
    db: Session,
    project_id: int,
    current_user: User,
    payload: ModelConfigCreate
):
    # 1. Verify project ownership
    stmt = select(Project).where(
        Project.id == project_id,
        Project.user_id == current_user.id
    )

    project = db.execute(stmt).scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # 2. Prepare model configuration
    model_config = ModelConfig(
        project_id=project.id,
        provider=payload.provider,
        model_name=payload.model_name,
        api_base_url=(
            str(payload.api_base_url)
            if payload.api_base_url else None
        ),
        config=payload.config,
        is_active=payload.is_active
    )

    # 3. Save to database
    try:
        db.add(model_config)
        db.commit()
        db.refresh(model_config)

    except Exception:
        db.rollback()
        raise

    return model_config


def list_model_configs(
    db: Session,
    project_id: int,
    current_user: User
):
    # Verify project ownership
    project_stmt = select(Project).where(
        Project.id == project_id,
        Project.user_id == current_user.id
    )

    project = db.execute(project_stmt).scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # Fetch model configurations
    stmt = (
        select(ModelConfig)
        .where(ModelConfig.project_id == project_id)
        .order_by(ModelConfig.created_at.desc())
    )

    model_configs = db.execute(stmt).scalars().all()

    return model_configs


def get_model_config(
    db: Session,
    model_id: int,
    current_user: User
):
    stmt = (
        select(ModelConfig)
        .join(Project, ModelConfig.project_id == Project.id)
        .where(
            ModelConfig.id == model_id,
            Project.user_id == current_user.id
        )
    )

    model_config = db.execute(stmt).scalar_one_or_none()

    if not model_config:
        raise HTTPException(
            status_code=404,
            detail="Model configuration not found"
        )

    return model_config


def update_model_config(
    db: Session,
    model_id: int,
    current_user: User,
    payload: ModelConfigUpdate
):
    stmt = (
        select(ModelConfig)
        .join(Project, ModelConfig.project_id == Project.id)
        .where(
            ModelConfig.id == model_id,
            Project.user_id == current_user.id
        )
    )

    model_config = db.execute(stmt).scalar_one_or_none()

    if not model_config:
        raise HTTPException(
            status_code=404,
            detail="Model configuration not found"
        )

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if field == "api_base_url" and value is not None:
            value = str(value)

        setattr(model_config, field, value)

    try:
        db.commit()
        db.refresh(model_config)

    except Exception:
        db.rollback()
        raise

    return model_config


def delete_model_config(
    db: Session,
    model_id: int,
    current_user: User
):
    stmt = (
        select(ModelConfig)
        .join(Project, ModelConfig.project_id == Project.id)
        .where(
            ModelConfig.id == model_id,
            Project.user_id == current_user.id
        )
    )

    model_config = db.execute(stmt).scalar_one_or_none()

    if not model_config:
        raise HTTPException(
            status_code=404,
            detail="Model configuration not found"
        )

    try:
        db.delete(model_config)
        db.commit()

    except Exception:
        db.rollback()
        raise

    return {"message": "Model configuration deleted successfully"}