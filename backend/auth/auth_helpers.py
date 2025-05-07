from fastapi import (
    Form,
    HTTPException,
    status,
    Depends,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import (
    select,
    Result,
)
from datetime import timedelta

from core.models import (
    User,
    db_helper,
)
from core.config import settings
from .utils import validate_password
from .schemas import UserAuthSchema
from .utils import encode_jwt

TOKEN_TYPE_FIELD = "type"
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


async def validate_auth_user(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
    email: str = Form(),
    password: str = Form(),
):
    unauthed_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password.",
    )

    stmt = select(User).where(User.email == email)
    result: Result = await session.execute(statement=stmt)
    user: User = result.scalar()
    if not user:
        raise unauthed_exception

    if not validate_password(
        password=password,
        hashed_password=user.password_hash,
    ):
        raise unauthed_exception

    return user


def create_token(
    token_type: str,
    token_data: dict,
    expire_minutes: int = settings.auth.access_token_expire_minutes,
    expire_timedelta: timedelta | None = None,
):
    jwt_payload = {TOKEN_TYPE_FIELD: token_type}
    jwt_payload.update(token_data)
    return encode_jwt(
        payload=jwt_payload,
        expire_minutes=expire_minutes,
        expire_timedelta=expire_timedelta,
    )


def create_access_token(user: UserAuthSchema) -> str:
    jwt_payload = {
        "sub": "user",
        "email": user.email,
    }
    return create_token(
        token_type=ACCESS_TOKEN_TYPE,
        token_data=jwt_payload,
    )


def create_refresh_token(user: UserAuthSchema) -> str:
    jwt_payload = {
        "sub": "user",
    }
    return create_token(
        token_type=REFRESH_TOKEN_TYPE,
        token_data=jwt_payload,
    )
