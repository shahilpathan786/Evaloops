
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class EvaluationResultResponse(BaseModel):
    id: int
    experiment_id: int
    dataset_record_id: int

    actual_output: str | None

    scores: dict[str, float] = Field(default_factory=dict)

    latency_ms: float | None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
