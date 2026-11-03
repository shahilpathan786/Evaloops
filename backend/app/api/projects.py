from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Project, User

from app.schemas.project import ProjectCreate, ProjectRead


router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)

@router.post(
    "",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED
)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db)
):

    # 1. Check whether the user exists
    user = db.get(User, payload.user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # 2. Check for duplicate project names
    statement = select(Project.id).where(
        Project.user_id == payload.user_id,
        Project.name == payload.name
    )

    existing = db.scalar(statement)

    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail="Project already exists"
        )

    # 3. Create project object
    project = Project(**payload.model_dump())

    # 4. Add to session
    db.add(project)

    # 5. Commit transaction
    try:
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Project conflicts with an existing database constraint"
        ) from None

    # 6. Refresh object
    db.refresh(project)

    return project