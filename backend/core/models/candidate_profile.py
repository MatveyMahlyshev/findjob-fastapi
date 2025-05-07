from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy import (
    String,
    ForeignKey,
    Integer,
    Text,
)
from typing import TYPE_CHECKING


from . import Base
from .mixins import UserRelationMixin

if TYPE_CHECKING:
    from .candidate_profile_skill_association import CandidateProfileSkillAssociation


class CandidateProfile(UserRelationMixin, Base):
    _user_back_populates = "candidate_profile"

    surname: Mapped[str] = mapped_column(String(50))
    name: Mapped[str] = mapped_column(String(50))
    patronymic: Mapped[str | None] = mapped_column(String(50))
    age: Mapped[int] = mapped_column(Integer)
    about_candidate: Mapped[str | None] = mapped_column(Text)
    education: Mapped[str] = mapped_column(Text)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
    )

    profile_skills: Mapped[list["CandidateProfileSkillAssociation"]] = relationship(
        back_populates="candidate_profile"
    )
