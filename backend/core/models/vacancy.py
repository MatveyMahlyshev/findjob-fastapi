from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Text, ForeignKey
from typing import TYPE_CHECKING

from .base import Base
from .user import User
from .mixins import UserRelationMixin

if TYPE_CHECKING:
    from .vacancy_skill_association import VacancySkillAssociation
    from .vacancy_response import VacancyResponse


class Vacancy(Base):
    __tablename__ = "vacancies"

    title: Mapped[str] = mapped_column(nullable=False, index=True)
    company: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(Text(), nullable=False)
    hr_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), unique=False, nullable=False
    )

    vacancy_skills: Mapped[list["VacancySkillAssociation"]] = relationship(
        back_populates="vacancy",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    hr: Mapped["User"] = relationship(
        "User",
        back_populates="vacancy",
    )

    responses: Mapped[list["VacancyResponse"]] = relationship(
        back_populates="vacancy",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
