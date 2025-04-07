from sqlalchemy import (
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from .base import Base

if TYPE_CHECKING:
    from .profile import Profile
    from .skill import Skill


class ProfileSkillAssociation(Base):
    __tablename__ = "profile_skill_association"
    __table_args__ = (
        UniqueConstraint(
            "profile_id",
            "skill_id",
            name="idx_unique_order_product",
        ),
    )
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"))
    skill_id: Mapped[int] = mapped_column(ForeignKey("techskills.id"))

    profile: Mapped["Profile"] = relationship(back_populates="profile_skills")
    techskills: Mapped["Skill"] = relationship(back_populates="skill_profiles")
