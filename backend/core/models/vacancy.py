from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Text
from typing import TYPE_CHECKING

from .base import Base

if TYPE_CHECKING:
    from .vacancy_skill_association import VacancySkillAssociation


class Vacancy(Base):
    title: Mapped[str] = mapped_column(
        nullable=False,
        index=True,
    )
    company: Mapped[str] = mapped_column(
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text(),
        nullable=False,
    )

    vacancy_skills: Mapped[list["VacancySkillAssociation"]] = relationship(
        back_populates="vacancy",
    )
