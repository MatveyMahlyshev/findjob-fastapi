from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import JSON, Text, ForeignKey
from typing import TYPE_CHECKING
from .base import Base

if TYPE_CHECKING:
    from .skill import Skill

class SkillTest(Base):
    __tablename__ = "skill_tests"

    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"))

    question: Mapped[str] = mapped_column(Text, unique=True)
    options: Mapped[list[str]] = mapped_column(JSON)
    correct_option_index: Mapped[int] = mapped_column()

    skill: Mapped["Skill"] = relationship(back_populates="tests")
