from fastapi import (
    Form,
    HTTPException,
    status,
    Depends,
)
from jwt.exceptions import InvalidTokenError
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import (
    select,
    Result,
)
from datetime import timedelta

from core.models import User, db_helper, CandidateProfile
from core.config import settings
from .utils import validate_password
from .schemas import UserAuthSchema
from .utils import encode_jwt, decode_jwt

TOKEN_TYPE_FIELD = "type"
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login/")


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
        "sub": user.email,
        "email": user.email,
    }
    return create_token(
        token_type=ACCESS_TOKEN_TYPE,
        token_data=jwt_payload,
    )


def create_refresh_token(user: UserAuthSchema) -> str:
    jwt_payload = {
        "sub": user.email,
    }
    return create_token(
        token_type=REFRESH_TOKEN_TYPE,
        token_data=jwt_payload,
    )


def get_current_token_payload(
    token: str = Depends(oauth2_scheme),
) -> dict:
    try:
        payload = decode_jwt(token=token)
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}",
        )
    return payload


def validate_token_type(
    payload: dict,
    token_type: str,
) -> bool:
    if payload.get(TOKEN_TYPE_FIELD) == token_type:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Error type of token.",
    )


async def get_user_by_token_sub(
    payload: dict,
    session: AsyncSession,
) -> UserAuthSchema:
    email: str | None = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token does not contain email",
        )

    stmt = select(User).where(User.email == email)
    result: Result = await session.execute(statement=stmt)
    user: User = result.scalar()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user

async def get_current_auth_user_for_refresh(
    payload: dict = Depends(get_current_token_payload),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),  # Добавляем session как зависимость
) -> UserAuthSchema:
    validate_token_type(payload=payload, token_type=REFRESH_TOKEN_TYPE)
    return await get_user_by_token_sub(payload=payload, session=session)  # Явно передаем session


def get_auth_user_from_token_of_type(token_type: str):
    def get_auth_user_from_token(
        payload: dict = Depends(get_current_token_payload),
        session: AsyncSession = Depends(db_helper.scoped_session_dependency), 
    ) -> UserAuthSchema:
        validate_token_type(
            payload=payload,
            token_type=token_type,
        )
        return get_user_by_token_sub(payload=payload, session=session)
    return get_auth_user_from_token

get_current_auth_user = get_auth_user_from_token_of_type(token_type=ACCESS_TOKEN_TYPE)
get_current_auth_user_for_refresh = get_auth_user_from_token_of_type(token_type=REFRESH_TOKEN_TYPE)

