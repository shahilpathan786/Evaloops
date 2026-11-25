
from sqlalchemy import select
from sqlalchemy.orm import Session

from fastapi import HTTPException

from app.models.evaluation_result import EvaluationResult
from app.models.experiment import Experiment
from app.models.project import Project
from app.models.user import User


def list_evaluation_results(
    db: Session,
    experiment_id: int,
    current_user: User,
    limit: int = 50,
    offset: int = 0
):
    # 1. Verify experiment ownership
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

    # 2. Fetch evaluation results
    stmt = (
        select(EvaluationResult)
        .where(
            EvaluationResult.experiment_id == experiment_id
        )
        .order_by(EvaluationResult.id.asc())
        .limit(limit)
        .offset(offset)
    )

    results = db.execute(stmt).scalars().all()

    return results



def get_evaluation_result(
    db: Session,
    result_id: int,
    current_user: User
):
    # 1. Fetch result and verify ownership
    result = db.execute(
        select(EvaluationResult)
        .join(
            Experiment,
            EvaluationResult.experiment_id == Experiment.id
        )
        .join(
            Project,
            Experiment.project_id == Project.id
        )
        .where(
            EvaluationResult.id == result_id,
            Project.user_id == current_user.id
        )
    ).scalar_one_or_none()

    # 2. Handle missing result
    if not result:
        raise HTTPException(
            status_code=404,
            detail="Evaluation result not found"
        )

    return result
