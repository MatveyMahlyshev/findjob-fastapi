from sqlalchemy import select
from sqlalchemy.orm import selectinload
from core.models import User, CandidateProfile, CandidateProfileSkillAssociation


def get_statement_for_candidate_profile(payload: dict):
    return (
        select(User)
        .options(
            selectinload(User.candidate_profile)
            .selectinload(CandidateProfile.profile_skills)
            .selectinload(CandidateProfileSkillAssociation.skill)
        )
        .where(User.email == payload["email"])
    )
