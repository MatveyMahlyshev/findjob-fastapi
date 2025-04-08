from pydantic import (
    BaseModel,
    EmailStr,
    SecretStr,
    ConfigDict,
    Field,
)
from typing import Annotated
from annotated_types import MinLen, MaxLen

from core.models.user import UserRole
from api_v1.profiles.schemas import ProfileBase


class UserBase(BaseModel):
    email: Annotated[EmailStr, MinLen(5), MaxLen(25)]
    role: UserRole = UserRole.CANDIDATE


class User(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class UserCreate(UserBase):
    password: SecretStr = Field(min_length=8, max_length=20)


class UserUpdate(UserCreate):
    pass


class CreateUserWithProfile(BaseModel):
    user: UserCreate
    profile: ProfileBase
    