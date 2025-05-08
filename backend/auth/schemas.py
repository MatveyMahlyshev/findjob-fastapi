from pydantic import (
    BaseModel,
    ConfigDict,
)


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"

class UserAuthSchema(BaseModel):
    model_config = ConfigDict(strict=True)
    email: str
    password: bytes