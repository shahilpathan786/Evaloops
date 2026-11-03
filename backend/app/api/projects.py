
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models import Project, User
from app.schemas.project import ProjectCreate, ProjectRead


router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post(
    "",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED
)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Check duplicate project for this user
    statement = select(Project.id).where(
        Project.user_id == current_user.id,
        Project.name == payload.name
    )

    existing = db.scalar(statement)

    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail="Project already exists"
        )

    # Automatically assign authenticated user
    project = Project(
        **payload.model_dump(),
        user_id=current_user.id
    )

    db.add(project)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Project conflicts with an existing database constraint"
        ) from None

    db.refresh(project)

    return project
