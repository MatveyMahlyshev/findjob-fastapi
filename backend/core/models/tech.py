from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)
from sqlalchemy import String
from .base import Base


class TechSkill(Base):
    title: Mapped[str] = mapped_column(
        String(25),
        nullable=False,
        unique=True,
    )
