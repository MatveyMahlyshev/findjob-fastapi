from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import (
    select,
    Result,
)
from fastapi import (
    HTTPException,
    status,
)

from .schemas import CreateUserWithProfile
from core.models import (
    User,
    Profile,
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

    user = User(
        email=user_profile.user.email,
        password_hash=user_profile.user.password.get_secret_value(),
        role=user_profile.user.role,
    )
    session.add(user)
    await session.flush()

    profile = Profile(
        surname=user_profile.profile.surname,
        name=user_profile.profile.name,
        patronymic=user_profile.profile.patronymic,
        about_candidate=user_profile.profile.about_candidate,
        user_id=user.id,
    )
    session.add(profile)

    await session.commit()

    return {
        "user": user,
        "profile": profile,
    }


# async def delete_user_with_profile
