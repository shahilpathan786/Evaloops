
from pydantic import BaseModel, ConfigDict, Field, field_validator


class DatasetCreate(BaseModel):
    project_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Dataset name cannot be empty")

        return value


class DatasetUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = value.strip()

        if not value:
            raise ValueError("Dataset name cannot be empty")

        return value


class DatasetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    name: str
    description: str | None
    created_at: object
    updated_at: object
