from pydantic import (
    BaseModel,
    ConfigDict,
)


class SkillBase(BaseModel):
    title: str


class Skill(SkillBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class SkillUpdate(SkillBase):
    new_title: str
