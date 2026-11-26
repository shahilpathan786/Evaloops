
from sqlalchemy import select

from app.db.session import sessionLocal
from app.models.experiment import Experiment
from app.models.dataset_record import DatasetRecord
from app.models.evaluation_result import EvaluationResult

from app.services.execution_persistence import (
    persist_execution_result,
)


def main():
    experiment_id = int(input("Enter experiment ID: "))
    record_id = int(input("Enter dataset record ID: "))

    db = sessionLocal()

    try:
        # 1. Fetch experiment and dataset record
        experiment = db.get(Experiment, experiment_id)
        record = db.get(DatasetRecord, record_id)

        if not experiment:
            print("Experiment not found")
            return

        if not record:
            print("Dataset record not found")
            return

        # 2. Prevent duplicate result insertion
        existing = db.execute(
            select(EvaluationResult).where(
                EvaluationResult.experiment_id == experiment.id,
                EvaluationResult.dataset_record_id == record.id,
            )
        ).scalar_one_or_none()

        if existing:
            print("This record already has an evaluation result.")
            return

        # 3. Simulate an execution result
        execution_result = {
            "input": record.input,
            "output": "This is a sample AI-generated output.",
            "latency_ms": 1250.5,
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150,
        }

        # 4. Persist result and trace
        saved = persist_execution_result(
            db=db,
            experiment=experiment,
            record=record,
            execution_result=execution_result,
        )

        print("\n--- PERSISTENCE SUCCESSFUL ---")
        print("Evaluation Result ID:", saved["evaluation_result"].id)
        print("Trace ID:", saved["trace"].id)
        print("Output:", saved["evaluation_result"].actual_output)
        print("Total Tokens:", saved["trace"].total_tokens)

        print("\n--- DATABASE VERIFICATION ---")

        saved_result = db.get(
            EvaluationResult,
            saved["evaluation_result"].id,
        )

        print("Evaluation Result Exists:", saved_result is not None)
        print("Experiment ID:", saved_result.experiment_id)
        print("Dataset Record ID:", saved_result.dataset_record_id)

    finally:
        db.close()




if __name__ == "__main__":
    main()
