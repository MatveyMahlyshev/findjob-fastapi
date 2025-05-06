import jwt
import bcrypt
from datetime import (
    timedelta,
    datetime,
)

from core.config import settings


def encode_jwt(
    payload: dict,
    private_key: str = settings.auth.private_key,
    algorithm: str = settings.auth.algorithm,
    expire_timedelta: timedelta | None = None,
    expire_minutes: int = settings.auth.access_token_expire_minutes,
):
    to_encode = payload.copy()
    now = datetime.utcnow()
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(
        exp=expire,
        iat=now,
    )
    encoded = jwt.encode(
        to_encode,
        private_key,
        algorithm=algorithm,
    )

    return encoded
