from fastapi import (
    APIRouter,
    Depends,
)
from fastapi.security import HTTPBearer


from .auth_helpers import (
    validate_auth_user,
    create_access_token,
    create_refresh_token,
    get_current_auth_user_for_refresh,
)
from .schemas import (
    TokenInfo,
    UserAuthSchema,
)
from core.models import (
    User,
)

http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(
    tags=["Auth"],
    dependencies=[Depends(http_bearer)],
)


@router.post("/login/", response_model=TokenInfo)
async def auth_user(
    user: UserAuthSchema = Depends(validate_auth_user),
) -> User:

    access_token = create_access_token(user=user)
    refresh_token = create_refresh_token(user=user)

    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh/", response_model=TokenInfo, response_model_exclude_none=True)
async def auth_refresh(user_data: dict = Depends(get_current_auth_user_for_refresh)):
    access_token = create_access_token(user=user_data["user"])
    return TokenInfo(access_token=access_token)
