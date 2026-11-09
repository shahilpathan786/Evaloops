
from sqlalchemy.orm import Session
from pydantic import ValidationError

from app.schemas.dataset_record import (
    DatasetRecordCreate,
    DatasetRecordBulkCreate,
)

from app.services.dataset_record import (
    bulk_create_dataset_records,
)


def validate_dataset_records(
    records: list[dict]
) -> list[DatasetRecordCreate]:

    validated_records = []
    validation_errors = []

    for index, record in enumerate(records, start=1):
        try:
            validated_record = DatasetRecordCreate.model_validate(
                record
            )

            validated_records.append(validated_record)

        except ValidationError as exc:
            validation_errors.append({
                "row": index,
                "errors": exc.errors()
            })

    if validation_errors:
        raise ValueError({
            "message": "Dataset validation failed",
            "details": validation_errors
        })

    return validated_records


def ingest_dataset_records(
    db: Session,
    dataset_id: int,
    current_user,
    records: list[dict]
):
    """
    Validate parsed records and insert them in bulk.
    """

    # Step 1: Validate all records
    validated_records = validate_dataset_records(records)

    # Step 2: Construct the existing bulk schema
    payload = DatasetRecordBulkCreate(
        records=validated_records
    )

    # Step 3: Reuse the existing database insertion service
    result = bulk_create_dataset_records(
        db=db,
        dataset_id=dataset_id,
        current_user=current_user,
        payload=payload
    )

    return result
