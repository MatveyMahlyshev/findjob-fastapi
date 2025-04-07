from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    Enum as SQLEnum,
    String,
    Boolean,
)
from enum import Enum
from typing import TYPE_CHECKING

from . import Base

if TYPE_CHECKING:
    from .candidate_profile import CandidateProfile



class UserRole(str, Enum):
    ADMIN = "admin"
    HR = "hr"
    CANDIDATE = "candidate"


class User(Base):
    email: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(
        String(25),
        nullable=False,
    )
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole),
        nullable=False,
        default=UserRole.CANDIDATE,
    )
    is_active = Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    candidate_profile = relationship(
        "CandidateProfile",
        back_populates="candidate_profile",
    )
