from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.dataset import Dataset
from app.models.project import Project
from app.models.dataset_record import DatasetRecord
from app.models.user import User
from sqlalchemy import select, func
import math
from app.schemas.dataset_record import DatasetRecordUpdate

from app.schemas.dataset_record import DatasetRecordCreate
from app.schemas.dataset_record import DatasetRecordBulkCreate


def create_dataset_record(
    db: Session,
    dataset_id: int,
    current_user: User,
    payload: DatasetRecordCreate
):
    # 1. Verify dataset exists and belongs to current user
    stmt = (
        select(Dataset)
        .join(Project, Dataset.project_id == Project.id)
        .where(
            Dataset.id == dataset_id,
            Project.user_id == current_user.id
        )
    )

    dataset = db.execute(stmt).scalar_one_or_none()

    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )

    # 2. Create dataset record
    record = DatasetRecord(
        dataset_id=dataset.id,
        input=payload.input,
        expected_output=payload.expected_output,
        context=payload.context
    )

    # 3. Save to database
    db.add(record)
    db.commit()
    db.refresh(record)

    return record

def get_dataset_records(
    db: Session,
    dataset_id: int,
    current_user: User,
    page: int = 1,
    limit: int = 10
):
    # 1. Verify dataset ownership
    stmt = (
        select(Dataset)
        .join(Project, Dataset.project_id == Project.id)
        .where(
            Dataset.id == dataset_id,
            Project.user_id == current_user.id
        )
    )

    dataset = db.execute(stmt).scalar_one_or_none()

    if not dataset:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    # 2. Calculate offset
    offset = (page - 1) * limit

    # 3. Get total number of records
    count_stmt = (
        select(func.count())
        .select_from(DatasetRecord)
        .where(DatasetRecord.dataset_id == dataset_id)
    )

    total = db.execute(count_stmt).scalar_one()

    # 4. Fetch paginated records
    records_stmt = (
        select(DatasetRecord)
        .where(DatasetRecord.dataset_id == dataset_id)
        .order_by(DatasetRecord.id.asc())
        .offset(offset)
        .limit(limit)
    )

    records = db.execute(records_stmt).scalars().all()

    # 5. Return paginated response
    return {
        "items": records,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": math.ceil(total / limit)
    }

def get_dataset_record(
    db: Session,
    dataset_id: int,
    record_id: int,
    current_user: User
):
    # 1. Verify dataset ownership
    stmt = (
        select(Dataset)
        .join(Project, Dataset.project_id == Project.id)
        .where(
            Dataset.id == dataset_id,
            Project.user_id == current_user.id
        )
    )

    dataset = db.execute(stmt).scalar_one_or_none()

    if not dataset:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    # 2. Find record inside the specified dataset
    record_stmt = (
        select(DatasetRecord)
        .where(
            DatasetRecord.id == record_id,
            DatasetRecord.dataset_id == dataset_id
        )
    )

    record = db.execute(record_stmt).scalar_one_or_none()

    if not record:
        raise HTTPException(
            status_code=404,
            detail="Dataset record not found"
        )

    return record

def update_dataset_record(
    db: Session,
    dataset_id: int,
    record_id: int,
    current_user: User,
    payload: DatasetRecordUpdate
):
    # 1. Verify dataset ownership
    stmt = (
        select(Dataset)
        .join(Project, Dataset.project_id == Project.id)
        .where(
            Dataset.id == dataset_id,
            Project.user_id == current_user.id
        )
    )

    dataset = db.execute(stmt).scalar_one_or_none()

    if not dataset:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    # 2. Find record inside the dataset
    record_stmt = (
        select(DatasetRecord)
        .where(
            DatasetRecord.id == record_id,
            DatasetRecord.dataset_id == dataset_id
        )
    )

    record = db.execute(record_stmt).scalar_one_or_none()

    if not record:
        raise HTTPException(
            status_code=404,
            detail="Dataset record not found"
        )

    # 3. Extract only fields sent by the user
    update_data = payload.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update"
        )

    # 4. Update provided fields
    for field, value in update_data.items():
        setattr(record, field, value)

    # 5. Save changes
    db.commit()
    db.refresh(record)

    return record

def delete_dataset_record(
    db: Session,
    dataset_id: int,
    record_id: int,
    current_user: User
):
    # 1. Verify dataset ownership
    stmt = (
        select(Dataset)
        .join(Project, Dataset.project_id == Project.id)
        .where(
            Dataset.id == dataset_id,
            Project.user_id == current_user.id
        )
    )

    dataset = db.execute(stmt).scalar_one_or_none()

    if not dataset:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    # 2. Find record inside the dataset
    record_stmt = (
        select(DatasetRecord)
        .where(
            DatasetRecord.id == record_id,
            DatasetRecord.dataset_id == dataset_id
        )
    )

    record = db.execute(record_stmt).scalar_one_or_none()

    if not record:
        raise HTTPException(
            status_code=404,
            detail="Dataset record not found"
        )

    # 3. Delete record
    db.delete(record)
    db.commit()

    return None

def bulk_create_dataset_records(
    db: Session,
    dataset_id: int,
    current_user: User,
    payload: DatasetRecordBulkCreate
):
    # 1. Verify dataset ownership
    stmt = (
        select(Dataset)
        .join(Project, Dataset.project_id == Project.id)
        .where(
            Dataset.id == dataset_id,
            Project.user_id == current_user.id
        )
    )

    dataset = db.execute(stmt).scalar_one_or_none()

    if not dataset:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    # 2. Convert schemas into SQLAlchemy objects
    records = [
        DatasetRecord(
            dataset_id=dataset.id,
            input=item.input,
            expected_output=item.expected_output,
            context=item.context
        )
        for item in payload.records
    ]

    # 3. Insert all records in one transaction
    try:
        db.add_all(records)
        db.commit()

    except Exception:
        db.rollback()
        raise


     # if some problem comes i need to remove this refresh work .
    # 4. Refresh generated database fields
    
    for record in records:
        db.refresh(record)

    return {
        "created_count": len(records),
        "items": records
    }