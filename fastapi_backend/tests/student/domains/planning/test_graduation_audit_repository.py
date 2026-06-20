import asyncio
import uuid
from datetime import datetime

from app.student.domains.discovery.models import Course, Program, University
from app.student.domains.planning.models import EdPlan, PlanCourse
from app.student.domains.planning.repositories.graduation_audit_repository import (
    GraduationAuditRepository,
)


class _ScalarResult:
    def __init__(self, values):
        self._values = values

    def all(self):
        return self._values


class _Result:
    def __init__(self, values):
        self._values = values

    def scalars(self):
        return _ScalarResult(self._values)

    def scalar_one_or_none(self):
        return self._values[0] if self._values else None


class _Session:
    def __init__(self, values):
        self.values = values
        self.statements = []

    async def execute(self, statement):
        self.statements.append(statement)
        return _Result(self.values)


def _catalog_objects():
    university = University(
        university_id=uuid.uuid4(),
        university_name="University of New Mexico-Main Campus",
        city="Albuquerque",
        state="NM",
        website="https://www.unm.edu",
    )
    program = Program(
        program_id=uuid.uuid4(),
        university_id=university.university_id,
        program_name="Computer Science",
        degree="Bachelor of Science",
        total_credit_hours=120,
        university=university,
    )
    course = Course(
        course_id=uuid.uuid4(),
        program_id=program.program_id,
        course_code="CS 101",
        course_name="Intro to Computer Science",
        credits=3,
        lecture_hours=3,
        lab_hours=0,
        recommended_year=1,
        recommended_semester="Fall",
        description="Foundational catalog course.",
        program=program,
    )
    return university, program, course


def _plan_with_course():
    university, program, course = _catalog_objects()
    plan = EdPlan(
        plan_id=uuid.uuid4(),
        user_id=42,
        university_id=university.university_id,
        program_id=program.program_id,
        plan_name="Primary Plan",
        description="Manual path through CS.",
        is_active=True,
        created_at=datetime(2026, 6, 10, 10, 0),
        updated_at=datetime(2026, 6, 10, 10, 0),
        university=university,
        program=program,
    )
    plan_course = PlanCourse(
        id=uuid.uuid4(),
        plan_id=plan.plan_id,
        course_id=course.course_id,
        planned_term_id=None,
        status="Planned",
        notes=None,
        plan=plan,
        course=course,
    )
    plan.courses = [plan_course]
    return plan, course


def test_graduation_audit_repository_loads_plan_context():
    plan, _ = _plan_with_course()
    repository = GraduationAuditRepository()
    session = _Session([plan])

    result = asyncio.run(repository.get_plan(session, plan.plan_id))

    assert result == plan
    assert result.program.program_name == "Computer Science"
    assert result.courses[0].course.course_code == "CS 101"
    assert len(session.statements) == 1


def test_graduation_audit_repository_lists_program_courses():
    _, program, course = _catalog_objects()
    repository = GraduationAuditRepository()
    session = _Session([course])

    result = asyncio.run(repository.list_program_courses(session, program.program_id))

    assert result == [course]
    assert result[0].program_id == program.program_id
    assert len(session.statements) == 1
