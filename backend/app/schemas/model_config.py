from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ModelConfigCreate(BaseModel):
    provider: str = Field(..., min_length=1, max_length=50)
    model_name: str = Field(..., min_length=1, max_length=150)
    api_base_url: HttpUrl | None = None
    config: dict = Field(default_factory=dict)
    is_active: bool = True


class ModelConfigUpdate(BaseModel):
    provider: str | None = Field(None, min_length=1, max_length=50)
    model_name: str | None = Field(None, min_length=1, max_length=150)
    api_base_url: HttpUrl | None = None
    config: dict | None = None
    is_active: bool | None = None


class ModelConfigResponse(BaseModel):
    id: int
    project_id: int
    provider: str
    model_name: str
    api_base_url: str | None
    config: dict
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)