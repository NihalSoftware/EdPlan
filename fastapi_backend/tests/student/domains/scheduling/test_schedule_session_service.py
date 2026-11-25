from __future__ import annotations

from datetime import datetime, time

import pytest

from app.student.domains.scheduling.engine import (
    ScheduleOption,
    ScheduleRankingMetadata,
    ScheduleRankingResult,
)
from app.student.domains.scheduling.schemas.decision import (
    DecisionContext,
    DecisionNextAction,
    DecisionReason,
    DecisionStatus,
    ScheduleDecisionResult,
)
from app.student.domains.scheduling.schemas.session import (
    CompareOptionsRequest,
    RegenerateSessionRequest,
    SelectOptionRequest,
    SessionHistoryAction,
    SessionIdRequest,
    SessionLifecycle,
    StartSessionRequest,
    TemporaryPreference,
)
from app.student.domains.scheduling.schemas.schedulepilot import ScheduleMeeting, ScheduleSection
from app.student.domains.scheduling.services.session_service import SchedulingSessionService


class _DecisionService:
    def __init__(self, status=DecisionStatus.OK):
        self.status = status
        self.calls = []

    async def decide_and_generate(self, db, request):
        self.calls.append(request)
        if self.status == DecisionStatus.NEEDS_INPUT:
            return ScheduleDecisionResult(
                status=DecisionStatus.NEEDS_INPUT,
                next_action=DecisionNextAction.ASK_FOR_PLAN,
                reason=DecisionReason.MULTIPLE_PLANS,
                context=DecisionContext(user_id=request.user_id),
                warnings=["Multiple active plans are available."],
            )
        option = _option("schedule-option-000001")
        return ScheduleDecisionResult(
            status=DecisionStatus.OK,
            next_action=DecisionNextAction.SHOW_RESULTS,
            reason=DecisionReason.GENERATION_COMPLETE,
            context=DecisionContext(
                user_id=request.user_id,
                resolved_plan_id=request.plan_id or "plan-1",
                resolved_term_id=request.term_id or "term-1",
                normalized_preferences=request.preferences,
            ),
            generation_metadata={"generated_count": 1},
            ranking_result=ScheduleRankingResult(
                options=[option],
                top_option=option,
                metadata=ScheduleRankingMetadata(
                    evaluated_candidates=1,
                    feasible_candidates=1,
                    ranked_candidates=1,
                    returned_candidates=1,
                    max_options=5,
                ),
            ),
            explanation="Generated schedules.",
        )


@pytest.mark.asyncio
async def test_session_creation_stores_generated_options_and_metadata():
    decision_service = _DecisionService()
    service = SchedulingSessionService(decision_service=decision_service)

    result = await service.start_session(
        object(),
        StartSessionRequest(
            user_id=1,
            plan_id="plan-1",
            term_id="term-1",
            preferences=[TemporaryPreference(key="morning_classes", value=True)],
        ),
    )

    state = result.session.state
    assert result.success is True
    assert state.lifecycle == SessionLifecycle.ACTIVE
    assert state.current_plan_id == "plan-1"
    assert state.current_term_id == "term-1"
    assert state.generated.ranking_order == ["schedule-option-000001"]
    assert state.current_next_action == DecisionNextAction.SHOW_RESULTS
    assert [entry.action for entry in state.history] == [
        SessionHistoryAction.CREATED,
        SessionHistoryAction.GENERATED,
    ]


@pytest.mark.asyncio
async def test_selection_and_comparison_do_not_regenerate():
    decision_service = _DecisionService()
    service = SchedulingSessionService(decision_service=decision_service)
    started = await service.start_session(object(), StartSessionRequest(user_id=1, plan_id="plan-1"))
    session_id = started.session.state.session_id

    selected = service.select_option(
        SelectOptionRequest(session_id=session_id, option_id="schedule-option-000001")
    )
    compared = service.compare_options(
        CompareOptionsRequest(
            session_id=session_id,
            option_ids=["schedule-option-000001", "schedule-option-000001"],
        )
    )

    assert len(decision_service.calls) == 1
    assert selected.session.state.selection.selected_option_id == "schedule-option-000001"
    assert compared.session.state.comparison.option_ids == [
        "schedule-option-000001",
        "schedule-option-000001",
    ]


@pytest.mark.asyncio
async def test_regenerate_merges_temporary_preferences_and_records_history():
    decision_service = _DecisionService()
    service = SchedulingSessionService(decision_service=decision_service)
    started = await service.start_session(
        object(),
        StartSessionRequest(
            user_id=1,
            plan_id="plan-1",
            preferences=[TemporaryPreference(key="time", value="morning")],
        ),
    )

    regenerated = await service.regenerate(
        object(),
        RegenerateSessionRequest(
            session_id=started.session.state.session_id,
            preferences=[TemporaryPreference(key="time", value="evening")],
        ),
    )

    assert len(decision_service.calls) == 2
    assert regenerated.session.state.preferences.temporary[0].value == "evening"
    assert regenerated.session.state.history[-1].action == SessionHistoryAction.REGENERATED


@pytest.mark.asyncio
async def test_undo_restores_previous_selection_state():
    service = SchedulingSessionService(decision_service=_DecisionService())
    started = await service.start_session(object(), StartSessionRequest(user_id=1, plan_id="plan-1"))
    session_id = started.session.state.session_id
    service.select_option(
        SelectOptionRequest(session_id=session_id, option_id="schedule-option-000001")
    )

    undone = service.undo_last_action(SessionIdRequest(session_id=session_id))

    assert undone.session.state.selection.selected_option_id is None
    assert undone.session.state.history[-1].action == SessionHistoryAction.UNDONE


@pytest.mark.asyncio
async def test_reset_and_close_update_lifecycle_without_schema_persistence():
    service = SchedulingSessionService(decision_service=_DecisionService())
    started = await service.start_session(object(), StartSessionRequest(user_id=1, plan_id="plan-1"))
    session_id = started.session.state.session_id

    reset = service.reset_session(SessionIdRequest(session_id=session_id))
    closed = service.close_session(SessionIdRequest(session_id=session_id))

    assert reset.session.state.generated.options == []
    assert closed.session.state.lifecycle == SessionLifecycle.CLOSED
    assert closed.session.state.closed_at is not None


@pytest.mark.asyncio
async def test_waiting_for_input_session_tracks_pending_action():
    service = SchedulingSessionService(decision_service=_DecisionService(DecisionStatus.NEEDS_INPUT))

    result = await service.start_session(object(), StartSessionRequest(user_id=1))

    assert result.session.state.lifecycle == SessionLifecycle.WAITING_FOR_INPUT
    assert result.session.state.current_next_action == DecisionNextAction.ASK_FOR_PLAN
    assert result.session.state.warnings == ["Multiple active plans are available."]


def _option(option_id: str) -> ScheduleOption:
    section = ScheduleSection(
        section_id="section-1",
        offering_id="offering-1",
        course_id="course-1",
        term_id="term-1",
        offering_type="Lecture",
        section_number="001",
        crn="12345",
        instruction_method="In Person",
        capacity=20,
        enrolled=5,
        available_seats=15,
        status="Open",
    )
    return ScheduleOption(
        option_id=option_id,
        rank=1,
        score=80,
        normalized_score=80,
        selected_sections=[section],
        selected_meetings=[
            ScheduleMeeting(
                meeting_id="meeting-1",
                section_id="section-1",
                weekday=1,
                start_time=time(9, 0),
                end_time=time(10, 0),
                meeting_type="Class",
                is_async=False,
            )
        ],
        explanation="Option explanation.",
        metadata={"created_at": datetime(2026, 6, 1, 9, 0).isoformat()},
    )
