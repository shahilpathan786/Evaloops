
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models import Project, User
from app.schemas.project import ProjectCreate, ProjectRead , ProjectUpdate
from fastapi import Query
from sqlalchemy import select



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


@router.get("", response_model=list[ProjectRead])
def get_projects(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    statement = (
        select(Project)
        .where(Project.user_id == current_user.id)
        .order_by(Project.created_at.desc(), Project.id.desc())
        .offset(skip)
        .limit(limit)
    )

    projects = db.scalars(statement).all()

    return projects



@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    statement = select(Project).where(
        Project.id == project_id,
        Project.user_id == current_user.id
    )

    project = db.scalar(statement)

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return project



@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Find project belonging to current user
    statement = select(Project).where(
        Project.id == project_id,
        Project.user_id == current_user.id
    )

    project = db.scalar(statement)

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # 2. Extract only fields supplied by client
    update_data = payload.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No fields provided for update"
        )

    # 3. Update project fields
    for field, value in update_data.items():
        setattr(project, field, value)

    # 4. Save changes
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Project conflicts with an existing database constraint"
        ) from None

    # 5. Refresh and return
    db.refresh(project)

    return project


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Find project belonging to current user
    statement = select(Project).where(
        Project.id == project_id,
        Project.user_id == current_user.id
    )

    project = db.scalar(statement)

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # 2. Delete project
    db.delete(project)

    # 3. Commit transaction
    db.commit()

    # 4. Return empty response
    return None



