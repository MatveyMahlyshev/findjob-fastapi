from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Result
from fastapi import HTTPException, status


from auth.utils import hash_password
from .schemas import CreateUserWithProfile, UserCreate
from core.models import User, CandidateProfile, UserRole
import exceptions

async def create_user(session: AsyncSession, user: UserCreate):
    email_exists = await session.execute(
        select(User.email).where(User.email == user.email)
    )
    if email_exists.scalar_one_or_none():
        raise exceptions.ConflictException.EMAIL_ALREADY_EXISTS
    new_user = User(
        email=user.email,
        password_hash=hash_password(user.password),
        role=user.role,
    )
    if user.role == UserRole.HR:
        session.add(new_user)
        await session.commit()

    return new_user


async def create_user_with_profile(
    session: AsyncSession, user_profile: CreateUserWithProfile
) -> dict:
    user = await create_user(session=session, user=user_profile.user)
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
    await session.flush()

    await session.commit()

    return {
        "user": user,
        "profile": profile,
    }
