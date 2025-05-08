from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from sqlalchemy import select, Result
from sqlalchemy.orm import selectinload

from auth.auth_helpers import get_current_token_payload
from core.models import User, CandidateProfile
from .schemas import CandidateProfileUser, SkillBase


async def get_candidate_profile_by_token(
    session: AsyncSession,
    payload: dict,
) -> CandidateProfileUser:
    """
    Получение профиля кандидата по данным из JWT-токена
    """
    if not (email := payload.get("sub")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token does not contain email",
        )

    # Оптимизированный запрос с жадной загрузкой
    stmt = (
        select(User)
        .options(
            selectinload(User.candidate_profile)
            .selectinload(CandidateProfile.skills)
        )
        .where(User.email == email)
    )
    
    user = (await session.execute(stmt)).scalar_one_or_none()
    
    if not user or not user.candidate_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found",
        )

    return CandidateProfileUser(
        email=user.email,
        name=user.name,
        surname=user.surname,
        patronymic=user.patronymic,
        age=user.candidate_profile.age,
        about_candidate=user.candidate_profile.about,
        education=user.candidate_profile.education,
        skills=[SkillBase(title=skill.title) for skill in user.candidate_profile.skills]
    )
