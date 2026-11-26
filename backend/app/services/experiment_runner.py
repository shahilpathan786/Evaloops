
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.experiment import Experiment
from app.models.dataset_record import DatasetRecord

from app.services.record_execution import execute_record
from app.services.execution_persistence import persist_execution_result


def run_experiment(
    db: Session,
    experiment: Experiment,
) -> Experiment:

    # 1. Only queued experiments can start
    if experiment.status != "queued":
        raise ValueError(
            "Only queued experiments can be executed"
        )

    # 2. Fetch dataset records
    records = db.execute(
        select(DatasetRecord)
        .where(
            DatasetRecord.dataset_id == experiment.dataset_id
        )
        .order_by(DatasetRecord.id)
    ).scalars().all()

    # 3. Get model and prompt configuration
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

    # 4. Mark experiment as running
    experiment.status = "running"
    experiment.started_at = datetime.now(timezone.utc)
    experiment.completed_at = None
    experiment.error_message = None

    db.commit()
    db.refresh(experiment)

    try:
        # 5. Execute every dataset record
        for record in records:

            execution_result = execute_record(
                model_name=model_config.model_name,
                record=record,
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # 6. Persist evaluation result and trace
            persist_execution_result(
                db=db,
                experiment=experiment,
                record=record,
                execution_result=execution_result,
            )

        # 7. Mark experiment as completed
        experiment.status = "completed"
        experiment.completed_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(experiment)

        return experiment

    except Exception as exc:

        # 8. Mark experiment as failed
        db.rollback()

        experiment = db.get(Experiment, experiment.id)

        experiment.status = "failed"
        experiment.error_message = str(exc)
        experiment.completed_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(experiment)

        raise
