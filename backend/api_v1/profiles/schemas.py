from pydantic import (
    BaseModel,
    ConfigDict,
)
from typing import Annotated
from annotated_types import (
    MinLen,
    MaxLen,
)


class ProfileBase(BaseModel):
    name: Annotated[str, MinLen(2), MaxLen(50)]
    surname: Annotated[str, MinLen(2), MaxLen(50)]
    patronymic: Annotated[str, MinLen(2), MaxLen(50)]
    about_candidate: str
    education: str


class Profile(ProfileBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    name: Annotated[str, MinLen(2), MaxLen(50)] | None
    surname: Annotated[str, MinLen(2), MaxLen(50)] | None
    patronymic: Annotated[str, MinLen(2), MaxLen(50)] | None
    about_candidate: str | None
