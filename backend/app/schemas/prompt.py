
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PromptCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    template: str = Field(..., min_length=1)
    system_message: str | None = None


class PromptUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150
    )

    template: str | None = Field(
        default=None,
        min_length=1
    )

    system_message: str | None = None


class PromptResponse(BaseModel):
    id: int
    project_id: int

    name: str
    version: int

    template: str
    system_message: str | None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
