from app.db.session import sessionLocal
from app.models.user import User
from app.schemas.dataset_record import DatasetRecordCreate
from app.services.dataset_record import create_dataset_record

db = sessionLocal()

try:
    # Get an existing user
    user = db.query(User).filter(User.id == 1).first()

    if not user:
        print("User not found!")
        raise SystemExit

    # Prepare test data
    payload = DatasetRecordCreate(
        input="What is machine learning?",
        expected_output="Machine learning is a subset of AI.",
        context="Basic AI knowledge"
    )

    # Call service directly
    record = create_dataset_record(
        db=db,
        dataset_id=1,  # Replace with your actual dataset ID
        current_user=user,
        payload=payload
    )

    print("Record created successfully!")
    print("Record ID:", record.id)
    print("Dataset ID:", record.dataset_id)
    print("Input:", record.input)

except Exception as e:
    db.rollback()
    print("Test failed:", e)

finally:
    db.close()