from fastapi import Form, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Result

from core.models import User, db_helper
from .utils import validate_password
from .schemas import UserAuthSchema
from . import dependencies
import exceptions


async def validate_auth_user(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
    email: str = Form(),
    password: str = Form(),
):

    stmt = select(User).where(User.email == email)
    result: Result = await session.execute(statement=stmt)
    user: User = result.scalar()
    if not user or not validate_password(
        password=password, hashed_password=user.password_hash
    ):
        raise exceptions.UnauthorizedException.INVALID_LOGIN_DATA

    return user


def create_access_token(user: UserAuthSchema) -> str:
    jwt_payload = {
        "sub": user.email,
        "email": user.email,
    }
    return dependencies.create_token(
        token_type=dependencies.TokenTypeFields.ACCESS_TOKEN_TYPE,
        token_data=jwt_payload,
    )


def create_refresh_token(user: UserAuthSchema) -> str:
    jwt_payload = {"sub": user.email}
    return dependencies.create_token(
        token_type=dependencies.TokenTypeFields.REFRESH_TOKEN_TYPE,
        token_data=jwt_payload,
    )


async def get_user_by_token_sub(payload: dict, session: AsyncSession) -> UserAuthSchema:
    email: str | None = payload.get("sub")
    if not email:
        raise exceptions.UnauthorizedException.NO_EMAIL

    stmt = select(User).where(User.email == email)
    result: Result = await session.execute(statement=stmt)
    user: User = result.scalar()

    if not user:
        raise exceptions.UnauthorizedException.INVALID_LOGIN_DATA
    return user


async def get_current_auth_user_for_refresh(
    payload: dict = Depends(dependencies.get_current_token_payload),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> UserAuthSchema:
    dependencies.validate_token_type(
        payload=payload, token_type=dependencies.TokenTypeFields.REFRESH_TOKEN_TYPE
    )
    return await get_user_by_token_sub(payload=payload, session=session)
