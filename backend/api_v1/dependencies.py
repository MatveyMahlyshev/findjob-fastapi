from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, Select
from fastapi import HTTPException, status
from core.models import User, CandidateProfile, CandidateProfileSkillAssociation

from typing import Tuple


async def get_user(
    session: AsyncSession, payload: dict, stmt: Select[Tuple[User]], user_role: str
) -> User:
    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="No email in token"
        )
    result = await session.execute(statement=stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user

async def get_statement_for_candidate_profile(payload: dict):
    return (
        select(User)
        .options(
            selectinload(User.candidate_profile)
            .selectinload(CandidateProfile.profile_skills)
            .selectinload(CandidateProfileSkillAssociation.skill)
        )
        .where(User.email == payload["email"])
    )
