from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class DatasetRecordCreate(BaseModel):
    input: str = Field(..., min_length=1)
    expected_output: str | None = None
    context: str | None = None


class DatasetRecordResponse(BaseModel):
    id: int
    dataset_id: int
    input: str
    expected_output: str | None
    context: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DatasetRecordListResponse(BaseModel):
    items: list[DatasetRecordResponse]
    total: int
    page: int
    limit: int
    total_pages: int


