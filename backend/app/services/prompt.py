
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from fastapi import HTTPException

from app.models.project import Project
from app.models.prompt import Prompt
from app.models.user import User

from app.schemas.prompt import PromptCreate, PromptUpdate


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


def list_prompts(
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

    # 2. Fetch all prompt versions
    stmt = (
        select(Prompt)
        .where(Prompt.project_id == project_id)
        .order_by(
            Prompt.name.asc(),
            Prompt.version.desc()
        )
    )

    prompts = db.execute(stmt).scalars().all()

    return prompts




def get_prompt(
    db: Session,
    prompt_id: int,
    current_user: User
):
    # 1. Fetch prompt and verify project ownership
    prompt = db.execute(
        select(Prompt)
        .join(Project, Prompt.project_id == Project.id)
        .where(
            Prompt.id == prompt_id,
            Project.user_id == current_user.id
        )
    ).scalar_one_or_none()

    # 2. Handle missing prompt
    if not prompt:
        raise HTTPException(
            status_code=404,
            detail="Prompt not found"
        )

    return prompt



def update_prompt(
    db: Session,
    prompt_id: int,
    current_user: User,
    payload: PromptUpdate
):
    # 1. Fetch prompt and verify ownership
    prompt = db.execute(
        select(Prompt)
        .join(Project, Prompt.project_id == Project.id)
        .where(
            Prompt.id == prompt_id,
            Project.user_id == current_user.id
        )
    ).scalar_one_or_none()

    if not prompt:
        raise HTTPException(
            status_code=404,
            detail="Prompt not found"
        )

    # 2. Extract provided fields
    updates = payload.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update"
        )

    # 3. Prevent null name or template
    if "name" in updates and updates["name"] is None:
        raise HTTPException(
            status_code=422,
            detail="Prompt name cannot be null"
        )

    if "template" in updates and updates["template"] is None:
        raise HTTPException(
            status_code=422,
            detail="Prompt template cannot be null"
        )

    # 4. Prepare new prompt values
    new_name = updates.get("name", prompt.name)
    new_template = updates.get("template", prompt.template)
    new_system_message = updates.get(
        "system_message",
        prompt.system_message
    )

    # 5. Find latest version for the target name
    latest_version = db.scalar(
        select(func.max(Prompt.version)).where(
            Prompt.project_id == prompt.project_id,
            Prompt.name == new_name
        )
    )

    next_version = (latest_version or 0) + 1

    # 6. Create a new immutable prompt version
    new_prompt = Prompt(
        project_id=prompt.project_id,
        name=new_name,
        version=next_version,
        template=new_template,
        system_message=new_system_message
    )

    # 7. Save to database
    try:
        db.add(new_prompt)
        db.commit()
        db.refresh(new_prompt)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Prompt version conflict. Please retry."
        )

    except Exception:
        db.rollback()
        raise

    return new_prompt


def delete_prompt(
    db: Session,
    prompt_id: int,
    current_user: User
):
    # 1. Fetch prompt and verify ownership
    prompt = db.execute(
        select(Prompt)
        .join(Project, Prompt.project_id == Project.id)
        .where(
            Prompt.id == prompt_id,
            Project.user_id == current_user.id
        )
    ).scalar_one_or_none()

    if not prompt:
        raise HTTPException(
            status_code=404,
            detail="Prompt not found"
        )

    # 2. Check whether an experiment uses this prompt
    experiment = db.scalar(
        select(Experiment.id)
        .where(Experiment.prompt_id == prompt_id)
        .limit(1)
    )

    if experiment is not None:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete prompt because it is used by an experiment"
        )

    # 3. Delete prompt
    try:
        db.delete(prompt)
        db.commit()

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Prompt is currently referenced by another resource"
        )

    except Exception:
        db.rollback()
        raise

