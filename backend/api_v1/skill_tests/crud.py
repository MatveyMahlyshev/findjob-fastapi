from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Result


from .schemas import SkillTestCreate
from api_v1.skills.crud import get_skill_by_id    
from core.models import SkillTest
import exceptions

async def create_skill_question(question: SkillTestCreate, session: AsyncSession) -> SkillTest:
    await get_skill_by_id(session=session, skill_id=question.skill_id)
    skill_test = SkillTest(**question.model_dump())
    session.add(skill_test)
    await session.commit()
    return skill_test

async def get_test_by_skill(skill_id: int, session: AsyncSession) -> list[SkillTest]:
    stmt = select(SkillTest).where(SkillTest.skill_id==skill_id)
    result: Result = await session.execute(statement=stmt)
    test = list(result.scalars().all())
    if test is None:
        raise exceptions.NotFoundException.TEST_NOT_FOUND
    return test