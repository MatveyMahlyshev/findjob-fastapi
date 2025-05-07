from sqlalchemy import (
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from .base import Base

if TYPE_CHECKING:
    from .candidate_profile import CandidateProfile
    from .skill import Skill


class CandidateProfileSkillAssociation(Base):
    __tablename__ = "candidate_profile_skill_association"
    __table_args__ = (
        UniqueConstraint(
            "candidate_profile_id",
            "skill_id",
            name="idx_unique_order_product",
        ),
    )
    candidate_profile_id: Mapped[int] = mapped_column(ForeignKey("candidateprofiles.id"))
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"))

    candidate_profile: Mapped["CandidateProfile"] = relationship(back_populates="profile_skills")
    skill: Mapped["Skill"] = relationship(back_populates="skill_profiles")
