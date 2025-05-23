from pydantic import BaseModel, ConfigDict

from api_v1.skills.schemas import SkillBase, Skill


class VacancySkillAssociationRead(BaseModel):
    skill: SkillBase
    model_config = ConfigDict(from_attributes=True)


class VacancyBase(BaseModel):
    title: str
    company: str
    description: str
    vacancy_skills: list[VacancySkillAssociationRead]
    model_config = ConfigDict(from_attributes=True)

class VacancyB(BaseModel):
    id: int
    title: str
    company: str
    description: str
    vacancy_skills: list[VacancySkillAssociationRead]
    responses: int
    model_config = ConfigDict(from_attributes=True)


class Vacancy(VacancyBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class VacancySkillAssociationCreate(BaseModel):
    skill: SkillBase


class VacancyCreate(BaseModel):
    title: str
    company: str
    description: str
    vacancy_skills: list[str]
