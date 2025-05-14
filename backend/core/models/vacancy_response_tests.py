from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from typing import Optional, TYPE_CHECKING

from . import Base

if TYPE_CHECKING:
    from .vacancy_response import VacancyResponse
    from .skill import Skill


class VacancyResponseTest(Base):
    __tablename__ = "vacancy_response_tests"

    response_id: Mapped[int] = mapped_column(
        ForeignKey("vacancy_responses.id", ondelete="CASCADE")
    )
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"))

    score: Mapped[Optional[float]] = mapped_column(nullable=True)
    is_completed: Mapped[bool] = mapped_column(default=False)

    response: Mapped["VacancyResponse"] = relationship(
        back_populates="tests", passive_deletes=True
    )
    skill: Mapped["Skill"] = relationship(
        back_populates="response_tests", passive_deletes=True
    )
