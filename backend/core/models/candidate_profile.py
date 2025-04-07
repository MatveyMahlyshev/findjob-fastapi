from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Integer, Text
from typing import TYPE_CHECKING


from . import Base
from .mixins import UserRelationMixin


class CandidateProfile(UserRelationMixin, Base):
    _user_back_populates = "profile"

    surname: Mapped[str] = mapped_column(String(50))
    name: Mapped[str] = mapped_column(String(50))
    patronymic: Mapped[str | None] = mapped_column(String(50))
    about_candidate: Mapped[Text | None]
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
    )

    # skills = relationship("TechSkill", secondary=) описать связь многие ко многим через доп класс
