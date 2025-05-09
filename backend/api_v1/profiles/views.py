from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from .schemas import CandidateProfileUser, CandidateProfileUpdate
from auth.auth_helpers import get_current_token_payload
from . import crud
from core.models import db_helper
from auth.auth_helpers import http_bearer
from api_v1.skills.schemas import SkillBase

router = APIRouter(
    tags=["Profile"],
    dependencies=[Depends(http_bearer)],
)


@router.get("/candidate/me/")
async def get_candidate_profile(
    payload: dict = Depends(get_current_token_payload),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> CandidateProfileUser:
    return await crud.get_user_with_profile_by_token(session=session, payload=payload)


@router.put("/candidate/me/edit/")
async def update_candidate_profile(
    data_to_update: CandidateProfileUpdate,
    payload: dict = Depends(get_current_token_payload),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> CandidateProfileUpdate:
    return await crud.update_candidate_profile(
        profile_data=data_to_update, session=session, payload=payload
    )


@router.put("/candidate/me/edit/skills/")
async def update_candidate_profile_skills(
    skills_in: List[SkillBase],
    payload: dict = Depends(get_current_token_payload),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> List[SkillBase]:
    return await crud.update_candidate_profile_skills(
        skills=skills_in, payload=payload, session=session
    )
