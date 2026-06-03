from __future__ import annotations

import uuid
from typing import List

from sqlalchemy import ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class University(Base):
    __tablename__ = "universities"

    university_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    university_name: Mapped[str] = mapped_column(String(256), nullable=False)
    city: Mapped[str | None] = mapped_column(String(128))
    state: Mapped[str | None] = mapped_column(String(64))
    website: Mapped[str | None] = mapped_column(String(512))

    programs: Mapped[List["Program"]] = relationship(back_populates="university")


class Program(Base):
    __tablename__ = "programs"

    program_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    university_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("universities.university_id"),
        index=True,
        nullable=False,
    )
    program_name: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    degree: Mapped[str | None] = mapped_column(String(128), index=True)
    total_credit_hours: Mapped[int | None] = mapped_column(Integer)

    university: Mapped[University] = relationship(back_populates="programs")
