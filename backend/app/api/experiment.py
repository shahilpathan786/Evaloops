
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User

from app.schemas.experiment import (
    ExperimentCreate,
    ExperimentResponse
)

from app.services.experiment import create_experiment
from app.api.deps import get_db, get_current_user

from app.services.experiment import (
    create_experiment,
    list_experiments,
    get_experiment
)



router = APIRouter(tags=["Experiments"])


@router.post(
    "/projects/{project_id}/experiments",
    response_model=ExperimentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_experiment_endpoint(
    project_id: int,
    payload: ExperimentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_experiment(
        db=db,
        project_id=project_id,
        current_user=current_user,
        payload=payload
    )


@router.get(
    "/projects/{project_id}/experiments",
    response_model=list[ExperimentResponse]
)
def get_project_experiments(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return list_experiments(
        db=db,
        project_id=project_id,
        current_user=current_user
    )


@router.get(
    "/experiments/{experiment_id}",
    response_model=ExperimentResponse
)
def get_experiment_endpoint(
    experiment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_experiment(
        db=db,
        experiment_id=experiment_id,
        current_user=current_user
    )

