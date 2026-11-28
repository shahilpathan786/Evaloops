
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.experiment import Experiment
from app.models.dataset_record import DatasetRecord
from app.models.evaluation_result import EvaluationResult

from app.services.record_execution import execute_record
from app.services.execution_persistence import (
    persist_execution_result,
    persist_execution_error,
)


def run_experiment(
    db: Session,
    experiment: Experiment,
) -> Experiment:

    # 1. Allow queued and failed experiments to execute
    if experiment.status not in ("queued", "failed"):
        raise ValueError(
            "Only queued or failed experiments can be executed"
        )

    # 2. Fetch dataset records
    records = db.execute(
        select(DatasetRecord)
        .where(
            DatasetRecord.dataset_id == experiment.dataset_id
        )
        .order_by(DatasetRecord.id)
    ).scalars().all()

    # 3. Identify records that have already succeeded
    successful_record_ids = set(
        db.execute(
            select(EvaluationResult.dataset_record_id)
            .where(
                EvaluationResult.experiment_id == experiment.id
            )
        ).scalars().all()
    )

    # 4. Get model and prompt configuration
    model_config = experiment.model_config
    prompt = experiment.prompt

    if model_config.provider.lower() != "groq":
        raise ValueError(
            "Currently, only Groq provider is supported"
        )

    temperature = model_config.config.get(
        "temperature", 0.7
    )

    max_tokens = model_config.config.get(
        "max_tokens", 1024
    )

    # 5. Mark experiment as running
    experiment.status = "running"
    experiment.started_at = datetime.now(timezone.utc)
    experiment.completed_at = None
    experiment.error_message = None

    db.commit()
    db.refresh(experiment)

    try:
        failed_records = []
        skipped_records = 0

        # 6. Execute dataset records independently
        for record in records:

            # Skip records that already succeeded
            if record.id in successful_record_ids:
                print(
                    f"Skipping record {record.id}: "
                    "already successfully processed"
                )
                skipped_records += 1
                continue

            try:
                execution_result = execute_record(
                    model_name=model_config.model_name,
                    record=record,
                    prompt=prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

            except Exception as exc:
                # Save failed execution trace
                persist_execution_error(
                    db=db,
                    experiment=experiment,
                    record=record,
                    error=exc,
                )

                failed_records.append(
                    f"Record {record.id}: {str(exc)}"
                )

                continue

            # Save successful execution result and trace
            persist_execution_result(
                db=db,
                experiment=experiment,
                record=record,
                execution_result=execution_result,
            )

        # 7. Determine final experiment status
        if failed_records:
            experiment.status = "failed"
            experiment.error_message = (
                f"{len(failed_records)} record(s) failed. "
                + "; ".join(failed_records)
            )
        else:
            experiment.status = "completed"
            experiment.error_message = None

        experiment.completed_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(experiment)

        print(f"Skipped records: {skipped_records}")
        print(f"Failed records: {len(failed_records)}")

        return experiment

    except Exception as exc:

        # Handle unexpected system or persistence errors
        db.rollback()

        experiment = db.get(Experiment, experiment.id)

        experiment.status = "failed"
        experiment.error_message = str(exc)
        experiment.completed_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(experiment)

        raise
