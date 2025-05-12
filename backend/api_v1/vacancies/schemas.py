from pydantic import BaseModel, ConfigDict

from api_v1.skills.schemas import SkillBase, Skill


class VacancySkillAssociationRead(BaseModel):
    skill: Skill
    model_config = ConfigDict(from_attributes=True)

class VacancyBase(BaseModel):
    title: str
    company: str
    description: str
    vacancy_skills: list[VacancySkillAssociationRead]


class Vacancy(VacancyBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

class VacancyCreate(VacancyBase):
    pass
