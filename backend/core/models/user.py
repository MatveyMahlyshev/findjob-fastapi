from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SQLEnum, String
from enum import Enum
from typing import TYPE_CHECKING

from . import Base

if TYPE_CHECKING:
    from .candidate_profile import CandidateProfile
    from .vacancy import Vacancy


class UserRole(str, Enum):
    ADMIN = "admin"
    HR = "hr"
    CANDIDATE = "candidate"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(String(25), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole), nullable=False, default=UserRole.CANDIDATE
    )

    candidate_profile: Mapped["CandidateProfile"] = relationship(
        "CandidateProfile", back_populates="user", uselist=False
    )

    vacancies: Mapped[list["Vacancy"]] = relationship("Vacancy", back_populates="hr")
