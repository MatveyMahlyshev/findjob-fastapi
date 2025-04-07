from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import (
    select,
    Result,
)

from .schemas import SkillCreate
from core.models import Skill


async def create_skill(
    session: AsyncSession,
    skill_in: SkillCreate,
) -> Skill:

    skill = Skill(**skill_in.model_dump())
    session.add(skill)
    await session.commit()

    return skill


async def get_skills(session: AsyncSession) -> list[Skill]:
    stmt = select(Skill).order_by(Skill.id)
    result: Result = await session.execute(statement=stmt)
    skills = list(result.scalars().all())
    return skills
