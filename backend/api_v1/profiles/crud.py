from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from sqlalchemy import select, Result
from sqlalchemy.orm import selectinload

from auth.auth_helpers import get_current_token_payload
from core.models import User, CandidateProfile, CandidateProfileSkillAssociation
from .schemas import CandidateProfileUser, SkillBase


from sqlalchemy.orm import selectinload


async def get_user_with_profile_by_token(
    session: AsyncSession,
    payload: dict,
) -> dict:
    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="No email in token"
        )

    stmt = (
        select(User)
        .options(
            selectinload(User.candidate_profile)
            .selectinload(CandidateProfile.profile_skills)
            .selectinload(CandidateProfileSkillAssociation.skill)
        )
        .where(User.email == email)
    )

    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if not user.candidate_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found for this user",
        )

    profile_data = {
        "email": user.email,
        "role": user.role.value,
        "name": user.candidate_profile.name,
        "surname": user.candidate_profile.surname,
        "patronymic": user.candidate_profile.patronymic,
        "age": user.candidate_profile.age,
        "about_candidate": user.candidate_profile.about_candidate,
        "education": user.candidate_profile.education,
        "skills": [
            {"title": assoc.skill.title, "id": assoc.skill.id}
            for assoc in user.candidate_profile.profile_skills
        ],
    }

    return profile_data
