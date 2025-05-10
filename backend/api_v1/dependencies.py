from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select
from typing import Tuple

from core.models import User
from exceptions import UnauthorizedException


async def get_user(
    session: AsyncSession, email: str, stmt: Select[Tuple[User]]
) -> User:
    if not email:
        raise UnauthorizedException.NO_EMAIL
    result = await session.execute(statement=stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise UnauthorizedException.INVALID_LOGIN_DATA
    return user
