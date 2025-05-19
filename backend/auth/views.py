from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from .auth_helpers import (
    validate_auth_user,
    create_access_token,
    create_refresh_token,
    get_current_auth_user_for_refresh,
    get_user_role,
)
from .schemas import TokenInfo, UserAuthSchema
from core.models import User
from .dependencies import http_bearer, get_current_token_payload
from core.models import db_helper


router = APIRouter(
    tags=["Auth"],
    dependencies=[Depends(http_bearer)],
)


@router.post("/login/", response_model=TokenInfo)
async def auth_user(user: UserAuthSchema = Depends(validate_auth_user)) -> User:

    access_token = create_access_token(user=user)
    refresh_token = create_refresh_token(user=user)

    return TokenInfo(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh/", response_model=TokenInfo, response_model_exclude_none=True)
async def auth_refresh(
    user: UserAuthSchema = Depends(get_current_auth_user_for_refresh),
):
    access_token = create_access_token(user=user)
    return TokenInfo(access_token=access_token)


@router.get("/role/")
async def get_role(
    payload: dict = Depends(get_current_token_payload),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await get_user_role(payload=payload, session=session)
