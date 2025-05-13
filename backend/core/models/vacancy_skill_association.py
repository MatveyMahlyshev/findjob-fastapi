from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint
from typing import TYPE_CHECKING

from .base import Base


if TYPE_CHECKING:
    from .skill import Skill
    from .vacancy import Vacancy


class VacancySkillAssociation(Base):
    __tablename__ = "vacancy_skill_associations"
    __table_args__ = (
        UniqueConstraint("vacancy_id", "skill_id", name="idx_unique_vacancy_skill"),
    )

    vacancy_id: Mapped[int] = mapped_column(
        ForeignKey("vacancies.id", ondelete="CASCADE")  # ВАЖНО: ondelete добавлен
    )
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"))

    vacancy: Mapped["Vacancy"] = relationship(back_populates="vacancy_skills")
    skill: Mapped["Skill"] = relationship(back_populates="skill_vacancies")
