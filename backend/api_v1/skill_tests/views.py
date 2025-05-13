from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import SkillTestCreate, SkillTest
from core.models import db_helper
from api_v1.skill_tests import crud

router = APIRouter(tags=["Skill tests"])


@router.post("/create/", response_model=SkillTest)
async def create_question_with_answers(
    question: SkillTestCreate,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.create_skill_question(question=question, session=session)


@router.get("/test/{skill_id}/", response_model=list[SkillTest])
async def get_test_by_skill(
    skill_id: int, session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    return await crud.get_test_by_skill(skill_id=skill_id, session=session)
