
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):

    email: EmailStr

    full_name: str = Field(min_length=2, max_length=100)

    password: str = Field(min_length=8, max_length=128)

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Full name cannot be empty")

        return value


class UserRead(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
