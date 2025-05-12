from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from fastapi import Depends
from jwt.exceptions import InvalidTokenError
from datetime import timedelta


from .utils import encode_jwt, decode_jwt
from core.config import settings
import exceptions
from core.models import User


class TokenTypeFields:
    TOKEN_TYPE_FIELD = "type"
    ACCESS_TOKEN_TYPE = "access"
    REFRESH_TOKEN_TYPE = "refresh"


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login/")
http_bearer = HTTPBearer(auto_error=False)


def get_current_token_payload(
    token: str = Depends(oauth2_scheme),
) -> dict:
    try:
        payload = decode_jwt(token=token)
    except InvalidTokenError:
        raise exceptions.UnauthorizedException.INVALID_TOKEN
    return payload


def create_token(
    token_type: str,
    token_data: dict,
    expire_minutes: int = settings.auth.access_token_expire_minutes,
    expire_timedelta: timedelta | None = None,
):
    jwt_payload = {TokenTypeFields.TOKEN_TYPE_FIELD: token_type}
    jwt_payload.update(token_data)
    return encode_jwt(
        payload=jwt_payload,
        expire_minutes=expire_minutes,
        expire_timedelta=expire_timedelta,
    )


def validate_token_type(payload: dict, token_type: str) -> bool:
    if payload.get(TokenTypeFields.TOKEN_TYPE_FIELD) == token_type:
        return True
    raise exceptions.UnauthorizedExceptions.ERROR_TOKEN_TYPE


async def check_access(user: User, role: str):
    if user.role != role:
        raise exceptions.AccessDeniesException.ACCESS_DENIED
