from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models import Dataset, Project, User
from app.schemas.dataset import DatasetCreate, DatasetRead
from fastapi import Query
from app.schemas.dataset import DatasetCreate, DatasetRead, DatasetUpdate
from app.services.dataset_record import create_dataset_record
from app.schemas.dataset_record import (
    DatasetRecordCreate,
    DatasetRecordResponse
)

from fastapi import Query

from app.schemas.dataset_record import DatasetRecordListResponse
from app.services.dataset_record import get_dataset_records
from app.services.dataset_record import get_dataset_record
from app.schemas.dataset_record import DatasetRecordUpdate
from app.services.dataset_record import update_dataset_record
from fastapi import Response
from app.services.dataset_record import delete_dataset_record

from app.schemas.dataset_record import DatasetRecordBulkCreate
from app.schemas.dataset_record import DatasetRecordBulkResponse

from app.services.dataset_record import bulk_create_dataset_records


router = APIRouter(
    prefix="/datasets",
    tags=["Datasets"]
)


@router.post(
    "/",
    response_model=DatasetRead,
    status_code=status.HTTP_201_CREATED
)
def create_dataset(
    payload: DatasetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Verify that the project belongs to the logged-in user
    project = db.scalar(
        select(Project).where(
            Project.id == payload.project_id,
            Project.user_id == current_user.id
        )
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # 2. Create dataset
    dataset = Dataset(
        project_id=project.id,
        name=payload.name,
        description=payload.description
    )

    db.add(dataset)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A dataset with this name already exists in this project"
        )

    db.refresh(dataset)

    return dataset

@router.get("/", response_model=list[DatasetRead])
def get_datasets(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    statement = (
        select(Dataset)
        .join(Project, Dataset.project_id == Project.id)
        .where(Project.user_id == current_user.id)
        .order_by(Dataset.created_at.desc(), Dataset.id.desc())
        .offset(skip)
        .limit(limit)
    )

    datasets = db.scalars(statement).all()

    return datasets

@router.get("/{dataset_id}", response_model=DatasetRead)
def get_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    statement = (
        select(Dataset)
        .join(Project, Dataset.project_id == Project.id)
        .where(
            Dataset.id == dataset_id,
            Project.user_id == current_user.id
        )
    )

    dataset = db.scalar(statement)

    if dataset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )

    return dataset


@router.patch("/{dataset_id}", response_model=DatasetRead)
def update_dataset(
    dataset_id: int,
    payload: DatasetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    statement = (
        select(Dataset)
        .join(Project, Dataset.project_id == Project.id)
        .where(
            Dataset.id == dataset_id,
            Project.user_id == current_user.id
        )
    )

    dataset = db.scalar(statement)

    if dataset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )

    update_data = payload.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No fields provided for update"
        )

    if "name" in update_data and update_data["name"] is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Dataset name cannot be null"
        )

    for field, value in update_data.items():
        setattr(dataset, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A dataset with this name already exists in this project"
        )

    db.refresh(dataset)

    return dataset



@router.delete(
    "/{dataset_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    statement = (
        select(Dataset)
        .join(Project, Dataset.project_id == Project.id)
        .where(
            Dataset.id == dataset_id,
            Project.user_id == current_user.id
        )
    )

    dataset = db.scalar(statement)

    if dataset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )

    db.delete(dataset)
    db.commit()

    return None

@router.post(
    "/{dataset_id}/records",
    response_model=DatasetRecordResponse,
    status_code=status.HTTP_201_CREATED
)
def create_record(
    dataset_id: int,
    payload: DatasetRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_dataset_record(
        db=db,
        dataset_id=dataset_id,
        current_user=current_user,
        payload=payload
    )


@router.get(
    "/{dataset_id}/records",
    response_model=DatasetRecordListResponse
)
def list_dataset_records(
    dataset_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_dataset_records(
        db=db,
        dataset_id=dataset_id,
        current_user=current_user,
        page=page,
        limit=limit
    )

@router.get(
    "/{dataset_id}/records/{record_id}",
    response_model=DatasetRecordResponse
)
def retrieve_dataset_record(
    dataset_id: int,
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_dataset_record(
        db=db,
        dataset_id=dataset_id,
        record_id=record_id,
        current_user=current_user
    )


@router.patch(
    "/{dataset_id}/records/{record_id}",
    response_model=DatasetRecordResponse
)
def update_record(
    dataset_id: int,
    record_id: int,
    payload: DatasetRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_dataset_record(
        db=db,
        dataset_id=dataset_id,
        record_id=record_id,
        current_user=current_user,
        payload=payload
    )


@router.delete(
    "/{dataset_id}/records/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response
)
def delete_record(
    dataset_id: int,
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    delete_dataset_record(
        db=db,
        dataset_id=dataset_id,
        record_id=record_id,
        current_user=current_user
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post(
    "/{dataset_id}/records/bulk",
    response_model=DatasetRecordBulkResponse,
    status_code=status.HTTP_201_CREATED
)
def bulk_create_records(
    dataset_id: int,
    payload: DatasetRecordBulkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return bulk_create_dataset_records(
        db=db,
        dataset_id=dataset_id,
        current_user=current_user,
        payload=payload
    )