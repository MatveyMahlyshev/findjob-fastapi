from fastapi import (
    APIRouter,
    Depends,
)
from fastapi.security import HTTPBearer
from datetime import timedelta

from core.config import settings
from .auth_helpers import (
    validate_auth_user,
    create_access_token,
    create_refresh_token,
)
from .schemas import (
    TokenInfo,
    UserAuthSchema,
)
from core.models import (
    User,
)

http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(prefix="/auth", tags=["Auth"], dependencies=[Depends(http_bearer)])


@router.post("/login", response_model=TokenInfo)
async def auth_user(
    user: UserAuthSchema = Depends(validate_auth_user),
) -> User:

    access_token = create_access_token(user=user)
    refresh_token = create_refresh_token(user=user)

    access_token_expires = timedelta(minutes=settings.auth.access_token_expire_minutes)
    refresh_token_expires = timedelta(days=settings.auth.refresh_token_expire_days)

    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=int(access_token_expires.total_seconds()),
        refresh_expires_in=int(refresh_token_expires.total_seconds()),
    )
