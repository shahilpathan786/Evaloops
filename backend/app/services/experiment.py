
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.project import Project
from app.models.dataset import Dataset
from app.models.dataset_record import DatasetRecord
from app.models.model_config import ModelConfig
from app.models.prompt import Prompt
from app.models.experiment import Experiment
from app.models.user import User

from app.schemas.experiment import ExperimentCreate , ExperimentUpdate


def create_experiment(
    db: Session,
    project_id: int,
    current_user: User,
    payload: ExperimentCreate
):
    # 1. Verify project ownership
    project = db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
    ).scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # 2. Verify dataset belongs to this project
    dataset = db.execute(
        select(Dataset).where(
            Dataset.id == payload.dataset_id,
            Dataset.project_id == project_id
        )
    ).scalar_one_or_none()

    if not dataset:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found in this project"
        )

    # 3. Verify model configuration belongs to this project
    model_config = db.execute(
        select(ModelConfig).where(
            ModelConfig.id == payload.model_config_id,
            ModelConfig.project_id == project_id
        )
    ).scalar_one_or_none()

    if not model_config:
        raise HTTPException(
            status_code=404,
            detail="Model configuration not found in this project"
        )

    # 4. Verify optional prompt belongs to this project
    if payload.prompt_id is not None:
        prompt = db.execute(
            select(Prompt).where(
                Prompt.id == payload.prompt_id,
                Prompt.project_id == project_id
            )
        ).scalar_one_or_none()

        if not prompt:
            raise HTTPException(
                status_code=404,
                detail="Prompt not found in this project"
            )

    # 5. Count dataset records
    total_records = db.scalar(
        select(func.count(DatasetRecord.id)).where(
            DatasetRecord.dataset_id == dataset.id
        )
    )

    # 6. Create experiment
    experiment = Experiment(
        project_id=project_id,
        dataset_id=dataset.id,
        model_config_id=model_config.id,
        prompt_id=payload.prompt_id,
        status="queued",
        total_records=total_records,
        started_at=None,
        completed_at=None
    )

    # 7. Save to database
    try:
        db.add(experiment)
        db.commit()
        db.refresh(experiment)

    except Exception:
        db.rollback()
        raise

    return experiment



def list_experiments(
    db: Session,
    project_id: int,
    current_user: User
):
    # 1. Verify project ownership
    project = db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
    ).scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # 2. Fetch experiments
    stmt = (
        select(Experiment)
        .where(Experiment.project_id == project_id)
        .order_by(Experiment.created_at.desc())
    )

    experiments = db.execute(stmt).scalars().all()

    return experiments



def get_experiment(
    db: Session,
    experiment_id: int,
    current_user: User
):
    experiment = db.execute(
        select(Experiment)
        .join(Project, Experiment.project_id == Project.id)
        .where(
            Experiment.id == experiment_id,
            Project.user_id == current_user.id
        )
    ).scalar_one_or_none()

    if not experiment:
        raise HTTPException(
            status_code=404,
            detail="Experiment not found"
        )

    return experiment



def update_experiment(
    db: Session,
    experiment_id: int,
    current_user: User,
    payload: ExperimentUpdate
):
    # 1. Fetch experiment and verify ownership
    experiment = db.execute(
        select(Experiment)
        .join(Project, Experiment.project_id == Project.id)
        .where(
            Experiment.id == experiment_id,
            Project.user_id == current_user.id
        )
    ).scalar_one_or_none()

    if not experiment:
        raise HTTPException(
            status_code=404,
            detail="Experiment not found"
        )

    # 2. Only queued experiments can be updated
    if experiment.status != "queued":
        raise HTTPException(
            status_code=400,
            detail="Only queued experiments can be updated"
        )

    # 3. Extract only fields provided by the user
    updates = payload.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update"
        )

    project_id = experiment.project_id

    # 4. Update dataset if provided
    if "dataset_id" in updates:
        if updates["dataset_id"] is None:
            raise HTTPException(
                status_code=422,
                detail="Dataset ID cannot be null"
            )

        dataset = db.execute(
            select(Dataset).where(
                Dataset.id == updates["dataset_id"],
                Dataset.project_id == project_id
            )
        ).scalar_one_or_none()

        if not dataset:
            raise HTTPException(
                status_code=404,
                detail="Dataset not found in this project"
            )

        experiment.dataset_id = dataset.id

        # Recalculate record count
        experiment.total_records = db.scalar(
            select(func.count(DatasetRecord.id)).where(
                DatasetRecord.dataset_id == dataset.id
            )
        )

    # 5. Update model configuration if provided
    if "model_config_id" in updates:
        if updates["model_config_id"] is None:
            raise HTTPException(
                status_code=422,
                detail="Model configuration ID cannot be null"
            )

        model_config = db.execute(
            select(ModelConfig).where(
                ModelConfig.id == updates["model_config_id"],
                ModelConfig.project_id == project_id
            )
        ).scalar_one_or_none()

        if not model_config:
            raise HTTPException(
                status_code=404,
                detail="Model configuration not found in this project"
            )

        experiment.model_config_id = model_config.id

    # 6. Update optional prompt if provided
    if "prompt_id" in updates:
        if updates["prompt_id"] is None:
            experiment.prompt_id = None

        else:
            prompt = db.execute(
                select(Prompt).where(
                    Prompt.id == updates["prompt_id"],
                    Prompt.project_id == project_id
                )
            ).scalar_one_or_none()

            if not prompt:
                raise HTTPException(
                    status_code=404,
                    detail="Prompt not found in this project"
                )

            experiment.prompt_id = prompt.id

    # 7. Save changes
    try:
        db.commit()
        db.refresh(experiment)

    except Exception:
        db.rollback()
        raise

    return experiment



def delete_experiment(
    db: Session,
    experiment_id: int,
    current_user: User
):
    # 1. Fetch experiment and verify ownership
    experiment = db.execute(
        select(Experiment)
        .join(Project, Experiment.project_id == Project.id)
        .where(
            Experiment.id == experiment_id,
            Project.user_id == current_user.id
        )
    ).scalar_one_or_none()

    if not experiment:
        raise HTTPException(
            status_code=404,
            detail="Experiment not found"
        )

    # 2. Check experiment status
    if experiment.status not in ["queued", "failed"]:
        raise HTTPException(
            status_code=400,
            detail="Only queued or failed experiments can be deleted"
        )

    # 3. Delete experiment
    try:
        db.delete(experiment)
        db.commit()

    except Exception:
        db.rollback()
        raise





