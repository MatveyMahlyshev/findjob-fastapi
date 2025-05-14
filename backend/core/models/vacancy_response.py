from enum import Enum
from sqlalchemy import Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey
import datetime
from typing import Optional, TYPE_CHECKING

from .base import Base

if TYPE_CHECKING:
    from .vacancy import Vacancy
    from .candidate_profile import CandidateProfile
    from .vacancy_response_tests import VacancyResponseTest


class VacancyResponseStatus(str, Enum):
    pending = "pending"
    test_sent = "test_sent"
    completed = "completed"
    rejected = "rejected"
    accepted = "accepted"


class VacancyResponse(Base):
    __tablename__ = "vacancy_responses"
    __table_args__ = (
        UniqueConstraint(
            "candidate_profile_id", "vacancy_id", name="idx_unique_profile_vacancy"
        ),
    )
    candidate_profile_id: Mapped[int] = mapped_column(
        ForeignKey("candidate_profiles.id", ondelete="CASCADE")
    )
    vacancy_id: Mapped[int] = mapped_column(
        ForeignKey("vacancies.id", ondelete="CASCADE")
    )

    created_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.utcnow
    )

    status: Mapped[VacancyResponseStatus] = mapped_column(
        SQLEnum(VacancyResponseStatus, name="vacancy_response_status"),
        default=VacancyResponseStatus.pending,
        nullable=False,
    )

    test_link: Mapped[Optional[str]] = mapped_column(nullable=True)

    candidate_profile: Mapped["CandidateProfile"] = relationship(
        back_populates="vacancy_responses", passive_deletes=True
    )
    vacancy: Mapped["Vacancy"] = relationship(
        back_populates="responses", passive_deletes=True
    )
    tests: Mapped[list["VacancyResponseTest"]] = relationship(
        back_populates="response",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
