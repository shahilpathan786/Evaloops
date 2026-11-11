
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


ExperimentStatus = Literal[
    "queued",
    "running",
    "completed",
    "failed",
    "cancelled"
]


class ExperimentCreate(BaseModel):
    dataset_id: int = Field(..., gt=0)
    model_config_id: int = Field(..., gt=0)
    prompt_id: int | None = Field(default=None, gt=0)


class ExperimentResponse(BaseModel):
    id: int
    project_id: int
    dataset_id: int
    model_config_id: int
    prompt_id: int | None

    status: ExperimentStatus
    total_records: int
    error_message: str | None

    started_at: datetime | None
    completed_at: datetime | None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExperimentStatusUpdate(BaseModel):
    status: ExperimentStatus
