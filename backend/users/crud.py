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
)


async def create_user_with_profile(
    session: AsyncSession, user_profile: CreateUserWithProfile
) -> dict:
    stmt = select(User.email)
    result: Result = await session.execute(statement=stmt)
    user_emails = set(result.scalars().all())
    if user_profile.user.email in user_emails:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists.",
        )
    hashpwd = hash_password(user_profile.user.password)
    user = User(
        email=user_profile.user.email,
        password_hash=hashpwd,
        role=user_profile.user.role,
    )
    session.add(user)
    await session.flush()

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

    await session.commit()

    return {
        "user": user,
        "profile": profile,
    }
