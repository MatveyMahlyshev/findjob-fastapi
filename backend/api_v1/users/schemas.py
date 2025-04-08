from pydantic import BaseModel, EmailStr, SecretStr, ConfigDict
from typing import Annotated

from annotated_types import MinLen, MaxLen

from core.models.user import UserRole

class UserBase(BaseModel):
    email: Annotated[EmailStr, MinLen(5), MaxLen(25)]
    role: UserRole = UserRole.CANDIDATE

class User(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

class UserCreate(UserBase):
    password: Annotated[SecretStr, MinLen(8), MaxLen(25)]


class UserUpdate(UserBase, UserCreate):
    pass


