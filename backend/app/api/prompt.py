
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User

from app.schemas.prompt import (
    PromptCreate,
    PromptUpdate,
    PromptResponse
)


from app.services.prompt import (
    create_prompt,
    list_prompts,
    get_prompt,
    update_prompt,
    delete_prompt
)



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




@router.get(
    "/projects/{project_id}/prompts",
    response_model=list[PromptResponse]
)
def get_project_prompts(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return list_prompts(
        db=db,
        project_id=project_id,
        current_user=current_user
    )



@router.get(
    "/prompts/{prompt_id}",
    response_model=PromptResponse
)
def get_prompt_endpoint(
    prompt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_prompt(
        db=db,
        prompt_id=prompt_id,
        current_user=current_user
    )



@router.patch(
    "/prompts/{prompt_id}",
    response_model=PromptResponse
)
def update_prompt_endpoint(
    prompt_id: int,
    payload: PromptUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_prompt(
        db=db,
        prompt_id=prompt_id,
        current_user=current_user,
        payload=payload
    )



@router.delete(
    "/prompts/{prompt_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_prompt_endpoint(
    prompt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    delete_prompt(
        db=db,
        prompt_id=prompt_id,
        current_user=current_user
    )
