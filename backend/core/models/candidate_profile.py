from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)
from sqlalchemy import (
    String,
    Boolean,
    ForeignKey,
    Integer,
    Text
)
from typing import TYPE_CHECKING


from . import Base


class CandidateProfile(Base):
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
    )
    surname: Mapped[str] = mapped_column(String(50))
    name: Mapped[str] = mapped_column(String(50))
    patronymic: Mapped[str] = mapped_column(String(50))
    about_candidate: Mapped[Text] = mapped_column(Text)


    # skills = relationship("TechSkill", secondary=) описать связь многие ко многим через доп класс
