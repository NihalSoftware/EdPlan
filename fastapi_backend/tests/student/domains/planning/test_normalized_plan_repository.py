import asyncio
import uuid
from datetime import date, datetime

from app.student.domains.discovery.models import Course, Program, University
from app.student.domains.planning.models import EdPlan, PlanCourse
from app.student.domains.planning.repositories.normalized_plan_repository import (
    NormalizedPlanRepository,
    PlanCourseRepository,
)
from app.student.domains.scheduling.models import AcademicTerm


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
        self.added = []
        self.flush_count = 0
        self.deleted = []

    async def execute(self, statement):
        self.statements.append(statement)
        return _Result(self.values)

    def add(self, model):
        self.added.append(model)

    async def flush(self):
        self.flush_count += 1

    async def delete(self, model):
        self.deleted.append(model)


def _catalog_objects():
    university = University(
        university_id=uuid.uuid4(),
        university_name="Northern New Mexico College",
        city="Espanola",
        state="New Mexico",
        website="https://www.nnmc.edu/",
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
    term = AcademicTerm(
        term_id=uuid.uuid4(),
        term_name="Fall 2026",
        start_date=date(2026, 8, 17),
        end_date=date(2026, 12, 11),
        is_active=True,
    )
    return university, program, course, term


def _plan_with_course():
    university, program, course, term = _catalog_objects()
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
        planned_term_id=term.term_id,
        status="Planned",
        notes="Take early.",
        plan=plan,
        course=course,
        planned_term=term,
    )
    plan.courses = [plan_course]
    return plan, plan_course, course, term


def test_normalized_plan_repository_lists_plans_with_catalog_context():
    plan, _, course, term = _plan_with_course()
    repository = NormalizedPlanRepository()
    session = _Session([plan])

    result = asyncio.run(repository.list_plans(session, user_id=42, is_active=True))

    assert result[0]["plan_id"] == str(plan.plan_id)
    assert result[0]["program"]["program_name"] == "Computer Science"
    assert result[0]["courses"][0]["course"]["course_code"] == "CS 101"
    assert result[0]["courses"][0]["planned_term"]["term_name"] == "Fall 2026"
    assert result[0]["term_credit_totals"] == [
        {
            "planned_term_id": str(term.term_id),
            "term_name": "Fall 2026",
            "credits": course.credits,
        }
    ]
    assert "legacy_education_plan_id" not in result[0]
    assert len(session.statements) == 1


def test_normalized_plan_repository_rejects_invalid_uuid_without_query():
    repository = NormalizedPlanRepository()
    session = _Session([])

    result = asyncio.run(repository.get_plan_by_id(session, "not-a-uuid"))

    assert result is None
    assert session.statements == []


def test_plan_course_repository_lists_courses_for_plan():
    plan, plan_course, _, _ = _plan_with_course()
    repository = PlanCourseRepository()
    session = _Session([plan_course])

    result = asyncio.run(repository.list_plan_courses(session, str(plan.plan_id)))

    assert result[0]["id"] == str(plan_course.id)
    assert result[0]["plan_id"] == str(plan.plan_id)
    assert result[0]["status"] == "Planned"
    assert result[0]["course"]["course_name"] == "Intro to Computer Science"
    assert len(session.statements) == 1


def test_plan_course_repository_can_clear_planned_term():
    _, plan_course, _, _ = _plan_with_course()
    repository = PlanCourseRepository()

    result = asyncio.run(
        repository.update_plan_course(
            plan_course,
            planned_term_id=None,
            update_planned_term=True,
            status="Completed",
            notes=None,
            update_notes=True,
        )
    )

    assert result.planned_term_id is None
    assert result.status == "Completed"
    assert result.notes is None
