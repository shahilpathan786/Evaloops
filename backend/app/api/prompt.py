
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User

from app.schemas.prompt import (
    PromptCreate,
    PromptResponse
)

from app.services.prompt import create_prompt


router = APIRouter(tags=["Prompts"])


@router.post(
    "/projects/{project_id}/prompts",
    response_model=PromptResponse,
    status_code=status.HTTP_201_CREATED
)
def create_prompt_endpoint(
    project_id: int,
    payload: PromptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_prompt(
        db=db,
        project_id=project_id,
        current_user=current_user,
        payload=payload
    )
