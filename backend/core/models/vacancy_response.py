from enum import Enum
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey
import datetime
from typing import Optional, TYPE_CHECKING

from .base import Base

if TYPE_CHECKING:
    from .vacancy import Vacancy
    from .candidate_profile import CandidateProfile


class VacancyResponseStatus(str, Enum):
    pending = "pending"
    test_sent = "test_sent"
    completed = "completed"
    rejected = "rejected"
    accepted = "accepted"


class VacancyResponse(Base):

    candidate_profile_id: Mapped[int] = mapped_column(
        ForeignKey("candidate_profiles.id")
    )
    vacancy_id: Mapped[int] = mapped_column(ForeignKey("vacancies.id"))

    created_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.utcnow
    )

    status: Mapped[VacancyResponseStatus] = mapped_column(
        SQLEnum(VacancyResponseStatus, name="vacancy_response_status"),
        default=VacancyResponseStatus.pending,
        nullable=False,
    )

    test_link: Mapped[Optional[str]] = mapped_column(nullable=True)

    candidate: Mapped["CandidateProfile"] = relationship(
        back_populates="vacancy_responses"
    )
    vacancy: Mapped["Vacancy"] = relationship(back_populates="responses")
