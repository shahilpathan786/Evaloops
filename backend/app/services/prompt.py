
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from fastapi import HTTPException

from app.models.project import Project
from app.models.prompt import Prompt
from app.models.user import User

from app.schemas.prompt import PromptCreate


def create_prompt(
    db: Session,
    project_id: int,
    current_user: User,
    payload: PromptCreate
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

    # 2. Find the latest version of this prompt
    latest_version = db.scalar(
        select(func.max(Prompt.version)).where(
            Prompt.project_id == project_id,
            Prompt.name == payload.name
        )
    )

    # 3. Assign the next version
    next_version = (latest_version or 0) + 1

    # 4. Create prompt
    prompt = Prompt(
        project_id=project_id,
        name=payload.name,
        version=next_version,
        template=payload.template,
        system_message=payload.system_message
    )

    # 5. Save to database
    try:
        db.add(prompt)
        db.commit()
        db.refresh(prompt)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Prompt version conflict. Please retry."
        )

    except Exception:
        db.rollback()
        raise

    return prompt
