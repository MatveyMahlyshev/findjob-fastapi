from pydantic import BaseModel, Field, Json, ConfigDict
from typing import TypedDict

class SkillTestBase(BaseModel):
    skill_id: int
    question: str
    options: list[str] = Field(..., min_items=2)


class SkillTest(SkillTestBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class SkillTestCreate(SkillTestBase):
    correct_option_index: int

class QuestionAnswer(TypedDict):
    question_id: int
    answer_id: int


class SkillTestAnswers(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    skill_id: int
    info: QuestionAnswer
    response_id: int
