from pydantic import BaseModel, EmailStr, ConfigDict

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    # Add fields required only during creation here, e.g.:
    # password: str
    pass

class UserRead(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)