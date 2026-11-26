
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.evalution_result import EvaluationResultResponse
from app.services.evalution_result import (
    list_evaluation_results,
    get_evaluation_result,
)

router = APIRouter(tags=["Evaluation Results"])


@router.get(
    "/experiments/{experiment_id}/results",
    response_model=list[EvaluationResultResponse],
)
def read_evaluation_results(
    experiment_id: int,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_evaluation_results(
        db=db,
        experiment_id=experiment_id,
        current_user=current_user,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/evaluation-results/{result_id}",
    response_model=EvaluationResultResponse,
)
def read_evaluation_result(
    result_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_evaluation_result(
        db=db,
        result_id=result_id,
        current_user=current_user,
    )
