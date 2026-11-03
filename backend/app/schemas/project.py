
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProjectCreate(BaseModel):

    name: str = Field(min_length=1, max_length=120)

    description: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Project name cannot be empty")

        return value


class ProjectUpdate(BaseModel):

    name: str | None = Field(default=None, min_length=1, max_length=120)

    description: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        if value is None:
            return value

        value = value.strip()

        if not value:
            raise ValueError("Project name cannot be empty")

        return value


class ProjectRead(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    description: str | None
    created_at: object
    updated_at: object
