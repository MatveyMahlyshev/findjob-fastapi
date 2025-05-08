from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from core.models import User, CandidateProfile, CandidateProfileSkillAssociation
from .schemas import CandidateProfileUser, CandidateProfileUpdate


from sqlalchemy.orm import selectinload


async def get_user(session: AsyncSession, payload: dict) -> User:
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
    return user


async def get_user_with_profile_by_token(
    session: AsyncSession, payload: dict
) -> CandidateProfileUser:

    user = await get_user(session=session, payload=payload)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if not user.candidate_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found for this user",
        )

    return {
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


async def update_candidate_profile(
    profile_data: CandidateProfileUpdate, session: AsyncSession, payload: dict
):
    user_profile = await get_user(session=session, payload=payload)
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    user_profile.email = profile_data.email
    user_profile.name = profile_data.name
    user_profile.candidate_profile.surname = profile_data.surname
    user_profile.candidate_profile.patronymic = profile_data.patronymic
    user_profile.candidate_profile.age = profile_data.age
    user_profile.candidate_profile.about_candidate = profile_data.about_candidate
    user_profile.candidate_profile.education = profile_data.education
    # user_profile.candidate_profile.profile_skills = profile_data.skills

    await session.commit()

    return {
        "email": user_profile.email,
        "role": user_profile.role.value,
        "name": user_profile.candidate_profile.name,
        "surname": user_profile.candidate_profile.surname,
        "patronymic": user_profile.candidate_profile.patronymic,
        "age": user_profile.candidate_profile.age,
        "about_candidate": user_profile.candidate_profile.about_candidate,
        "education": user_profile.candidate_profile.education,
        "skills": [
            {"title": assoc.skill.title, "id": assoc.skill.id}
            for assoc in user_profile.candidate_profile.profile_skills
        ],
    }
