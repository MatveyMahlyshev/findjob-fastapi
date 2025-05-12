import jwt
import bcrypt
from datetime import timedelta, datetime

from core.config import settings


def encode_jwt(
    payload: dict,
    private_key: str = settings.auth.private_key.read_text(),
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
    encoded = jwt.encode(to_encode, private_key, algorithm=algorithm)

    return encoded


def decode_jwt(
    token,
    public_key: str = settings.auth.public_key.read_text(),
    algorithm: str = settings.auth.algorithm,
):
    decoded = jwt.decode(token, public_key, algorithms=[algorithm])
    return decoded


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    hashed: bytes = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed.decode("utf-8")


def validate_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        password.encode(),
        hashed_password.encode()
    )