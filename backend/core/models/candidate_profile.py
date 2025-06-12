from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy import (
    String,
    Integer,
    Text,
)
from typing import TYPE_CHECKING


from . import Base
from .mixins import UserRelationMixin

if TYPE_CHECKING:
    from .candidate_profile_skill_association import CandidateProfileSkillAssociation
    from .vacancy_response import VacancyResponse


class CandidateProfile(UserRelationMixin, Base):
    __tablename__ = "candidate_profiles"

    _user_back_populates = "candidate_profile"
    _user_id_unique: bool = True

    surname: Mapped[str] = mapped_column(String(50))
    name: Mapped[str] = mapped_column(String(50))
    patronymic: Mapped[str | None] = mapped_column(String(50))
    age: Mapped[int] = mapped_column(Integer)
    about_candidate: Mapped[str | None] = mapped_column(Text)
    education: Mapped[str] = mapped_column(Text)

    profile_skills: Mapped[list["CandidateProfileSkillAssociation"]] = relationship(
        back_populates="candidate_profile"
    )

    vacancy_responses: Mapped[list["VacancyResponse"]] = relationship(
        back_populates="candidate_profile"
    )
