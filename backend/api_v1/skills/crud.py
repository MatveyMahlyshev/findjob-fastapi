from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import (
    select,
    Result,
)
from fastapi import HTTPException, status

from .schemas import SkillCreate
from core.models import Skill


async def create_skill(
    session: AsyncSession,
    skill_in: SkillCreate,
) -> Skill:

    skill = Skill(**skill_in.model_dump())
    skill.title = skill.title.lower().capitalize()
    session.add(skill)
    await session.commit()

    return skill


async def get_skills(session: AsyncSession) -> list[Skill]:
    stmt = select(Skill).order_by(Skill.id)
    result: Result = await session.execute(statement=stmt)
    skills = list(result.scalars().all())
    return skills


async def get_skill(session: AsyncSession, title: str) -> Skill:
    title = title.lower().capitalize()
    stmt = select(Skill).where(Skill.title == title)
    skill: Skill | None = await session.scalar(statement=stmt)
    if skill is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill {title} is not found.",
        )
    return skill


