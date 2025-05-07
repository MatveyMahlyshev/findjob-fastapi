from pydantic import (
    BaseModel,
    ConfigDict,
)
from typing import Annotated
from annotated_types import (
    MinLen,
    MaxLen,
)


class CandidateProfileBase(BaseModel):
    name: Annotated[str, MinLen(2), MaxLen(50)]
    surname: Annotated[str, MinLen(2), MaxLen(50)]
    patronymic: Annotated[str, MinLen(2), MaxLen(50)]
    age: int
    about_candidate: str
    education: str


class CandidateProfile(CandidateProfileBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class CandidateProfileCreate(CandidateProfileBase):
    pass


class CandidateProfileUpdate(CandidateProfileBase):
    name: Annotated[str, MinLen(2), MaxLen(50)] | None
    surname: Annotated[str, MinLen(2), MaxLen(50)] | None
    patronymic: Annotated[str, MinLen(2), MaxLen(50)] | None
    about_candidate: str | None
