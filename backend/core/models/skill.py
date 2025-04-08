from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy import String
from typing import TYPE_CHECKING
from .base import Base

if TYPE_CHECKING:
    from .profile_skill_association import ProfileSkillAssociation


class Skill(Base):
    title: Mapped[str] = mapped_column(
        String(25),
        nullable=False,
        unique=True,
        index=True
    )
    skill_profiles: Mapped[list["ProfileSkillAssociation"]] = relationship(
        back_populates="skill", 
    )
