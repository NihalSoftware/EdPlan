"""Unknown contact hours must survive ORM, discovery and scheduling serialization."""

from decimal import Decimal

import pytest
from sqlalchemy import Numeric

from app.student.domains.discovery.models import Course
from app.student.domains.discovery.schemas.course import CourseSummary
from app.student.domains.discovery.schemas.program import CourseSummary as ProgramCourse
from app.student.domains.scheduling.schemas.schedulepilot import ScheduleCourse


@pytest.mark.parametrize("model", [CourseSummary, ProgramCourse])
def test_discovery_hours_preserve_null_zero_and_fractional_values(model):
    base = {
        "course_id": "course",
        "program_id": "program",
        "course_code": "PT 1011",
        "course_name": "Intro to Pharmacy Technician",
        "credits": 3,
    }
    unknown = model(**base)
    assert unknown.model_dump()["lecture_hours"] is None
    assert unknown.model_dump()["lab_hours"] is None
    known = model(**base, lecture_hours=Decimal("3.5"), lab_hours=0)
    assert known.model_dump()["lecture_hours"] == 3.5
    assert known.model_dump()["lab_hours"] == 0


def test_scheduling_accepts_unknown_contact_hours():
    course = ScheduleCourse(
        plan_course_id="pc",
        plan_id="p",
        course_id="c",
        status="planned",
        course_code="PT 1011",
        course_name="Intro to Pharmacy Technician",
        credits=3,
        lecture_hours=None,
        lab_hours=None,
    )
    assert course.model_dump()["lecture_hours"] is None
    assert course.model_dump()["lab_hours"] is None


def test_orm_contact_hours_are_nullable_numeric_without_fabricated_defaults():
    for name in ("lecture_hours", "lab_hours"):
        column = Course.__table__.c[name]
        assert column.nullable
        assert isinstance(column.type, Numeric)
        assert column.server_default is None
