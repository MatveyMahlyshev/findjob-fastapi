from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import db_helper
from .schemas import CreateUserWithProfile
from . import crud

router = APIRouter(tags=["Users"])


@router.post(
    "/register/",
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_user_with_profile(
    user_profile: CreateUserWithProfile,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.create_user_with_profile(
        session=session,
        user_profile=user_profile,
    )
