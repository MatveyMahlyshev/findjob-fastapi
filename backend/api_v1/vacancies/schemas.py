from pydantic import BaseModel, ConfigDict

from api_v1.skills.schemas import SkillBase


class VacancyBase(BaseModel):
    title: str
    company: str
    description: str
    vacancy_skills: list[SkillBase]


class Vacancy(VacancyBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

class VacancyCreate(BaseModel):
    pass
