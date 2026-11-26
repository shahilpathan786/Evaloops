
from sqlalchemy.orm import Session

from app.models.experiment import Experiment
from app.models.dataset_record import DatasetRecord
from app.models.evaluation_result import EvaluationResult
from app.models.trace import Trace


def persist_execution_result(
    db: Session,
    experiment: Experiment,
    record: DatasetRecord,
    execution_result: dict,
):
    # 1. Verify that the record belongs to the experiment's dataset
    if record.dataset_id != experiment.dataset_id:
        raise ValueError(
            "Dataset record does not belong to this experiment"
        )

    # 2. Create evaluation result
    evaluation_result = EvaluationResult(
        experiment_id=experiment.id,
        dataset_record_id=record.id,
        actual_output=execution_result["output"],
        scores={},
        latency_ms=execution_result["latency_ms"],
    )

    # 3. Create execution trace
    trace = Trace(
        project_id=experiment.project_id,
        model_config_id=experiment.model_config_id,
        input=execution_result["input"],
        output=execution_result["output"],
        latency_ms=execution_result["latency_ms"],
        prompt_tokens=execution_result["prompt_tokens"],
        completion_tokens=execution_result["completion_tokens"],
        total_tokens=execution_result["total_tokens"],
        status="success",
    )

    # 4. Save both records in one transaction
    try:
        db.add_all([
            evaluation_result,
            trace,
        ])

        db.commit()

        db.refresh(evaluation_result)
        db.refresh(trace)

    except Exception:
        db.rollback()
        raise

    # 5. Return persisted records
    return {
        "evaluation_result": evaluation_result,
        "trace": trace,
    }
