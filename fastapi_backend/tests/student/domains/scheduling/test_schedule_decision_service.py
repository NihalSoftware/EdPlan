from __future__ import annotations

from datetime import date, time

import pytest

from app.student.domains.scheduling.schemas.decision import (
    DecisionNextAction,
    DecisionReason,
    DecisionStatus,
    ScheduleDecisionRequest,
)
from app.student.domains.scheduling.schemas.schedulepilot import (
    ScheduleCourse,
    ScheduleCourseOffering,
    ScheduleMeeting,
    ScheduleRetrievalContext,
    ScheduleRetrievalWarnings,
    ScheduleSection,
    ScheduleStudentPlan,
    ScheduleTerm,
)
from app.student.domains.scheduling.services.decision_service import ScheduleDecisionService


class _PlanRepository:
    def __init__(self, plans=None):
        self.plans = plans or []

    async def list_plans(self, db, *, user_id=None, is_active=None):
        return list(self.plans)


class _RetrievalService:
    def __init__(self, context):
        self.context = context
        self.calls = []

    async def build_context(self, db, *, user_id, plan_id):
        self.calls.append((db, user_id, plan_id))
        return self.context


@pytest.mark.asyncio
async def test_decision_service_resolves_single_active_plan_and_generates_options():
    service = ScheduleDecisionService(
        plan_repository=_PlanRepository(plans=[_plan_dict("plan-1")]),
        retrieval_service=_RetrievalService(_context(plan_id="plan-1")),
    )

    result = await service.decide_and_generate(
        object(),
        ScheduleDecisionRequest(user_id=1, preferences=[{"key": "morning_classes"}]),
    )

    assert result.status == DecisionStatus.OK
    assert result.next_action == DecisionNextAction.SHOW_RESULTS
    assert result.reason == DecisionReason.GENERATION_COMPLETE
    assert result.context.resolved_plan_id == "plan-1"
    assert result.context.resolved_term_id == "term-1"
    assert result.ranking_result is not None
    assert result.ranking_result.metadata.returned_candidates == 1
    assert result.explanation == "Generated schedules for Fall 2026 using your Primary Plan plan."


@pytest.mark.asyncio
async def test_decision_service_needs_input_for_multiple_active_plans():
    service = ScheduleDecisionService(
        plan_repository=_PlanRepository(plans=[_plan_dict("plan-1"), _plan_dict("plan-2")]),
        retrieval_service=_RetrievalService(_context()),
    )

    result = await service.decide_and_generate(object(), ScheduleDecisionRequest(user_id=1))

    assert result.status == DecisionStatus.NEEDS_INPUT
    assert result.next_action == DecisionNextAction.ASK_FOR_PLAN
    assert result.reason == DecisionReason.MULTIPLE_PLANS
    assert [plan.plan_id for plan in result.context.available_plans] == ["plan-1", "plan-2"]
    assert result.ranking_result is None


@pytest.mark.asyncio
async def test_decision_service_needs_input_when_no_active_plan_exists():
    service = ScheduleDecisionService(
        plan_repository=_PlanRepository(),
        retrieval_service=_RetrievalService(_context()),
    )

    result = await service.decide_and_generate(object(), ScheduleDecisionRequest(user_id=1))

    assert result.status == DecisionStatus.NEEDS_INPUT
    assert result.next_action == DecisionNextAction.ASK_FOR_PLAN
    assert result.reason == DecisionReason.NO_PLANS


@pytest.mark.asyncio
async def test_decision_service_fails_for_empty_plan():
    service = ScheduleDecisionService(
        retrieval_service=_RetrievalService(_context(courses=[])),
    )

    result = await service.decide_and_generate(
        object(),
        ScheduleDecisionRequest(user_id=1, plan_id="plan-1"),
    )

    assert result.status == DecisionStatus.FAILED
    assert result.reason == DecisionReason.EMPTY_PLAN
    assert result.next_action == DecisionNextAction.STOP


@pytest.mark.asyncio
async def test_decision_service_needs_term_when_planned_terms_are_ambiguous():
    service = ScheduleDecisionService(
        retrieval_service=_RetrievalService(
            _context(
                courses=[
                    _course(planned_term_id="term-1"),
                    _course(plan_course_id="pc-2", course_id="course-2", planned_term_id="term-2"),
                ],
                terms=[_term("term-1"), _term("term-2")],
            )
        ),
    )

    result = await service.decide_and_generate(
        object(),
        ScheduleDecisionRequest(user_id=1, plan_id="plan-1"),
    )

    assert result.status == DecisionStatus.NEEDS_INPUT
    assert result.next_action == DecisionNextAction.ASK_FOR_TERM
    assert result.reason == DecisionReason.MULTIPLE_POSSIBLE_TERMS


@pytest.mark.asyncio
async def test_decision_service_fails_when_no_offerings_exist():
    service = ScheduleDecisionService(
        retrieval_service=_RetrievalService(_context(offerings=[])),
    )

    result = await service.decide_and_generate(
        object(),
        ScheduleDecisionRequest(user_id=1, plan_id="plan-1"),
    )

    assert result.status == DecisionStatus.FAILED
    assert result.reason == DecisionReason.NO_OFFERINGS


@pytest.mark.asyncio
async def test_decision_service_fails_when_no_sections_exist():
    service = ScheduleDecisionService(
        retrieval_service=_RetrievalService(_context(sections=[])),
    )

    result = await service.decide_and_generate(
        object(),
        ScheduleDecisionRequest(user_id=1, plan_id="plan-1"),
    )

    assert result.status == DecisionStatus.FAILED
    assert result.reason == DecisionReason.NO_SECTIONS


@pytest.mark.asyncio
async def test_decision_service_generates_warning_for_missing_meetings():
    context = _context(
        meetings=[],
        warnings=ScheduleRetrievalWarnings(sections_without_meetings=["section-1"]),
    )
    service = ScheduleDecisionService(retrieval_service=_RetrievalService(context))

    result = await service.decide_and_generate(
        object(),
        ScheduleDecisionRequest(user_id=1, plan_id="plan-1"),
    )

    assert result.status == DecisionStatus.WARNING
    assert result.reason == DecisionReason.PARTIAL_SCHEDULING_DATA
    assert result.next_action == DecisionNextAction.REVIEW_WARNINGS
    assert result.warnings == ["Some sections are missing meeting information."]
    assert result.ranking_result is not None


@pytest.mark.asyncio
async def test_decision_service_applies_request_preferences_over_saved_and_defaults():
    service = ScheduleDecisionService(
        retrieval_service=_RetrievalService(_context()),
    )

    result = await service.decide_and_generate(
        object(),
        ScheduleDecisionRequest(
            user_id=1,
            plan_id="plan-1",
            system_defaults=[{"key": "time", "value": "afternoon"}],
            saved_preferences=[{"key": "time", "value": "morning"}],
            preferences=[{"key": "time", "value": "evening"}],
        ),
    )

    assert result.context.normalized_preferences == [{"key": "time", "value": "evening"}]


def _plan_dict(plan_id: str):
    return {
        "plan_id": plan_id,
        "user_id": 1,
        "university_id": "university-1",
        "program_id": "program-1",
        "plan_name": f"Plan {plan_id}",
        "description": None,
        "is_active": True,
    }


def _context(
    *,
    plan_id: str = "plan-1",
    courses=None,
    terms=None,
    offerings=None,
    sections=None,
    meetings=None,
    warnings=None,
):
    term = _term("term-1")
    course = _course()
    offering = ScheduleCourseOffering(
        offering_id="offering-1",
        course_id="course-1",
        term_id="term-1",
        offering_type="Lecture",
        course_code="CS 101",
        course_name="Intro",
        credits=3,
        term=term,
    )
    section = ScheduleSection(
        section_id="section-1",
        offering_id="offering-1",
        course_id="course-1",
        term_id="term-1",
        offering_type="Lecture",
        section_number="001",
        crn="12345",
        instruction_method="In Person",
        capacity=30,
        enrolled=10,
        available_seats=20,
        status="Open",
    )
    meeting = ScheduleMeeting(
        meeting_id="meeting-1",
        section_id="section-1",
        weekday=1,
        start_time=time(9, 0),
        end_time=time(10, 15),
        meeting_type="Class",
        is_async=False,
    )
    return ScheduleRetrievalContext(
        plan=ScheduleStudentPlan(
            plan_id=plan_id,
            user_id=1,
            university_id="university-1",
            program_id="program-1",
            plan_name="Primary Plan",
            is_active=True,
        ),
        courses=[course] if courses is None else courses,
        terms=[term] if terms is None else terms,
        offerings=[offering] if offerings is None else offerings,
        sections=[section] if sections is None else sections,
        meetings=[meeting] if meetings is None else meetings,
        warnings=warnings or ScheduleRetrievalWarnings(),
    )


def _term(term_id: str) -> ScheduleTerm:
    return ScheduleTerm(
        term_id=term_id,
        term_name="Fall 2026",
        start_date=date(2026, 8, 17),
        end_date=date(2026, 12, 11),
        is_active=True,
    )


def _course(
    *,
    plan_course_id: str = "pc-1",
    course_id: str = "course-1",
    planned_term_id: str | None = "term-1",
) -> ScheduleCourse:
    return ScheduleCourse(
        plan_course_id=plan_course_id,
        plan_id="plan-1",
        course_id=course_id,
        planned_term_id=planned_term_id,
        status="Planned",
        course_code="CS 101",
        course_name="Intro",
        credits=3,
        lecture_hours=3,
        lab_hours=0,
    )
