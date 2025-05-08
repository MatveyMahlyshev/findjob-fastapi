from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import (
    select,
    Result,
)
from fastapi import (
    HTTPException,
    status,
)
from auth.utils import hash_password
from .schemas import CreateUserWithProfile
from core.models import (
    User,
    CandidateProfile,
    Skill,
    CandidateProfileSkillAssociation,
)


async def create_user_with_profile(
    session: AsyncSession, user_profile: CreateUserWithProfile
) -> dict:
    # Проверка существования email
    email_exists = await session.execute(
        select(User.email).where(User.email == user_profile.user.email)
    )
    if email_exists.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists.",
        )

    # Создание пользователя
    user = User(
        email=user_profile.user.email,
        password_hash=hash_password(user_profile.user.password),
        role=user_profile.user.role,
    )
    session.add(user)
    await session.flush()

    # Валидация навыков
    if not user_profile.profile.skills:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No skills chosen."
        )

    # Создание профиля
    profile = CandidateProfile(
        surname=user_profile.profile.surname,
        name=user_profile.profile.name,
        patronymic=user_profile.profile.patronymic,
        age=user_profile.profile.age,
        about_candidate=user_profile.profile.about_candidate,
        user_id=user.id,
        education=user_profile.profile.education,
    )
    session.add(profile)
    await session.flush()

    # Добавление навыков
    for skill in user_profile.profile.skills:
        skill_obj = await session.get(Skill, skill.skill_id)
        if not skill_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Skill with id: {skill.skill_id} not available.",
            )

        association = CandidateProfileSkillAssociation(
            candidate_profile_id=profile.id,
            skill_id=skill.skill_id,
        )
        session.add(association)

    await session.commit()

    return {
        "user": user,
        "profile": profile,
    }
