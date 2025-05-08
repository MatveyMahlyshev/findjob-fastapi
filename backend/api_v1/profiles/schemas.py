from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
)
from typing import Annotated, List
from annotated_types import (
    MinLen,
    MaxLen,
)

from api_v1.skills.schemas import SkillBase


class CandidateProfileBase(BaseModel):
    name: Annotated[str, MinLen(2), MaxLen(50)]
    surname: Annotated[str, MinLen(2), MaxLen(50)]
    patronymic: Annotated[str, MinLen(2), MaxLen(50)]
    age: int
    about_candidate: str
    education: str
    skills: List[SkillBase]


class CandidateProfile(CandidateProfileBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

class CandidateProfileUser(BaseModel):
    email: Annotated[EmailStr, MinLen(5), MaxLen(25)]
    name: Annotated[str, MinLen(2), MaxLen(50)]
    surname: Annotated[str, MinLen(2), MaxLen(50)]
    patronymic: Annotated[str, MinLen(2), MaxLen(50)]
    age: int
    about_candidate: str
    education: str
    skills: List[SkillBase]


class CandidateProfileUpdate(CandidateProfileUser):
    pass

