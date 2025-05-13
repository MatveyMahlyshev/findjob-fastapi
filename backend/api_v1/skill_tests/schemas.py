from pydantic import BaseModel, Field, Json, ConfigDict


class SkillTestBase(BaseModel):
    skill_id: int
    question: str
    options: list[str] = Field(..., min_items=2)
    correct_option_index: int


class SkillTest(SkillTestBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class SkillTestCreate(SkillTestBase):
    pass
