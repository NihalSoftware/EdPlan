from __future__ import annotations

import uuid
from typing import List

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class University(Base):
    __tablename__ = "universities"
    __table_args__ = (
        UniqueConstraint(
            "university_name",
            "city",
            "state",
            name="universities_name_city_state_uk",
        ),
    )

    university_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    university_name: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(120), nullable=False)
    state: Mapped[str] = mapped_column(String(120), nullable=False)
    website: Mapped[str | None] = mapped_column(String(255))

    programs: Mapped[List["Program"]] = relationship(back_populates="university")


class Program(Base):
    __tablename__ = "programs"
    __table_args__ = (
        UniqueConstraint("program_id", "university_id", name="programs_program_university_uk"),
        UniqueConstraint(
            "university_id",
            "program_name",
            "degree",
            name="programs_university_name_degree_uk",
        ),
        CheckConstraint("total_credit_hours > 0", name="programs_total_credit_hours_chk"),
        Index("idx_programs_university_id", "university_id"),
    )

    program_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    university_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("universities.university_id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    program_name: Mapped[str] = mapped_column(String(255), nullable=False)
    degree: Mapped[str] = mapped_column(String(120), nullable=False)
    total_credit_hours: Mapped[int] = mapped_column(Integer, nullable=False)

    university: Mapped[University] = relationship(back_populates="programs")
    courses: Mapped[List["Course"]] = relationship(back_populates="program")


class Course(Base):
    __tablename__ = "courses"
    __table_args__ = (
        UniqueConstraint("program_id", "course_code", name="courses_program_code_uk"),
        CheckConstraint("credits > 0", name="courses_credits_chk"),
        CheckConstraint("lecture_hours >= 0 AND lab_hours >= 0", name="courses_hours_chk"),
        CheckConstraint(
            "recommended_year IS NULL OR recommended_year >= 1 AND recommended_year <= 8",
            name="courses_recommended_year_chk",
        ),
        CheckConstraint(
            "recommended_semester IS NULL OR recommended_semester IN "
            "('Fall', 'Spring', 'Summer', 'Winter')",
            name="courses_recommended_semester_chk",
        ),
        Index("idx_courses_course_code", "course_code"),
    )

    course_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    program_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("programs.program_id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    course_code: Mapped[str] = mapped_column(String(40), nullable=False)
    course_name: Mapped[str] = mapped_column(String(255), nullable=False)
    credits: Mapped[int] = mapped_column(Integer, nullable=False)
    lecture_hours: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    lab_hours: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    recommended_year: Mapped[int | None] = mapped_column(Integer)
    recommended_semester: Mapped[str | None] = mapped_column(String(20))
    description: Mapped[str | None] = mapped_column(Text)

    program: Mapped[Program] = relationship(back_populates="courses")
    prerequisite_links: Mapped[List["CoursePrerequisite"]] = relationship(
        back_populates="course",
        foreign_keys="CoursePrerequisite.course_id",
        cascade="all, delete-orphan",
    )
    required_by_links: Mapped[List["CoursePrerequisite"]] = relationship(
        back_populates="prerequisite_course",
        foreign_keys="CoursePrerequisite.prerequisite_course_id",
    )
    corequisite_links: Mapped[List["CourseCorequisite"]] = relationship(
        back_populates="course",
        foreign_keys="CourseCorequisite.course_id",
        cascade="all, delete-orphan",
    )
    corequired_by_links: Mapped[List["CourseCorequisite"]] = relationship(
        back_populates="corequisite_course",
        foreign_keys="CourseCorequisite.corequisite_course_id",
    )


class CoursePrerequisite(Base):
    __tablename__ = "course_prerequisites"
    __table_args__ = (
        UniqueConstraint(
            "course_id",
            "prerequisite_course_id",
            name="course_prerequisites_pair_uk",
        ),
        CheckConstraint(
            "course_id <> prerequisite_course_id",
            name="course_prerequisites_not_self_chk",
        ),
        Index("idx_course_prerequisites_course_id", "course_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("courses.course_id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    prerequisite_course_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("courses.course_id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )

    course: Mapped[Course] = relationship(
        back_populates="prerequisite_links",
        foreign_keys=[course_id],
    )
    prerequisite_course: Mapped[Course] = relationship(
        back_populates="required_by_links",
        foreign_keys=[prerequisite_course_id],
    )


class CourseCorequisite(Base):
    __tablename__ = "course_corequisites"
    __table_args__ = (
        UniqueConstraint(
            "course_id",
            "corequisite_course_id",
            name="course_corequisites_pair_uk",
        ),
        CheckConstraint(
            "course_id <> corequisite_course_id",
            name="course_corequisites_not_self_chk",
        ),
        Index("idx_course_corequisites_corequisite_course_id", "corequisite_course_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("courses.course_id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    corequisite_course_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("courses.course_id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )

    course: Mapped[Course] = relationship(
        back_populates="corequisite_links",
        foreign_keys=[course_id],
    )
    corequisite_course: Mapped[Course] = relationship(
        back_populates="corequired_by_links",
        foreign_keys=[corequisite_course_id],
    )
