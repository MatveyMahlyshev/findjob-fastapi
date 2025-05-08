from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession


from .schemas import CandidateProfileUser
from auth.auth_helpers import get_current_token_payload
from auth.schemas import UserAuthSchema
from . import crud
from core.models import db_helper
from auth.auth_helpers import http_bearer

router = APIRouter(
    tags=["Profile"],
    dependencies=[Depends(http_bearer)],
)


@router.get("/candidate/me/")
async def get_info_about_candidate(
    payload: dict = Depends(get_current_token_payload),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> CandidateProfileUser:
    return await crud.get_user_with_profile_by_token(
        session=session,
        payload=payload,
    )
