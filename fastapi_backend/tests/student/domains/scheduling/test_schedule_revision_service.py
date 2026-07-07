from __future__ import annotations

from datetime import datetime, time

import pytest

from app.student.domains.scheduling.engine import ScheduleOption
from app.student.domains.scheduling.schemas.revision import (
    LockSectionRequest,
    RestoreOriginalScheduleRequest,
    RevisionOperation,
    ScheduleRevisionRequest,
    UnlockSectionRequest,
)
from app.student.domains.scheduling.schemas.session import (
    GeneratedScheduleSet,
    SessionIdRequest,
    SessionLifecycle,
    SessionState,
    SchedulingSession,
)
from app.student.domains.scheduling.schemas.schedulepilot import ScheduleMeeting, ScheduleSection
from app.student.domains.scheduling.services.revision_service import ScheduleRevisionService
from app.student.domains.scheduling.services.session_service import SchedulingSessionService


def test_revision_engine_replaces_section_using_existing_alternative():
    service = _service_with_session()

    result = service.revise(
        ScheduleRevisionRequest(
            session_id="session-1",
            option_id="option-1",
            operation=RevisionOperation.REPLACE_SECTION,
            section_id="section-1",
            replacement_section_id="section-2",
        )
    )

    assert result.success is True
    assert result.revised_option is not None
    assert [section.section_id for section in result.revised_option.selected_sections] == [
        "section-2",
        "section-3",
    ]
    assert result.revision is not None
    assert result.revision.replaced_section_ids == ["section-1"]
    assert result.revision.added_section_ids == ["section-2"]
    assert result.revision.affected_course_ids == ["course-1"]
    assert result.revised_option.metadata["partial_regeneration"] is True


def test_revision_engine_respects_locked_sections():
    service = _service_with_session()
    service.lock_section(
        LockSectionRequest(
            session_id="session-1",
            section_id="section-1",
            course_id="course-1",
        )
    )

    with pytest.raises(ValueError, match="Locked sections cannot be revised"):
        service.revise(
            ScheduleRevisionRequest(
                session_id="session-1",
                option_id="option-1",
                operation=RevisionOperation.REPLACE_SECTION,
                section_id="section-1",
                replacement_section_id="section-2",
            )
        )


def test_revision_engine_unlocks_sections():
    service = _service_with_session()
    service.lock_section(LockSectionRequest(session_id="session-1", section_id="section-1"))

    result = service.unlock_section(
        UnlockSectionRequest(session_id="session-1", section_id="section-1")
    )

    assert result.session.state.locked_sections == []


def test_revision_engine_can_replace_instructor_delivery_and_meeting_time():
    service = _service_with_session()

    instructor = service.revise(
        ScheduleRevisionRequest(
            session_id="session-1",
            option_id="option-1",
            operation=RevisionOperation.REPLACE_INSTRUCTOR,
            section_id="section-1",
            instructor="Dr. Later",
        )
    )
    service = _service_with_session()
    delivery = service.revise(
        ScheduleRevisionRequest(
            session_id="session-1",
            option_id="option-1",
            operation=RevisionOperation.REPLACE_DELIVERY,
            section_id="section-1",
            instruction_method="Online",
        )
    )
    service = _service_with_session()
    meeting = service.revise(
        ScheduleRevisionRequest(
            session_id="session-1",
            option_id="option-1",
            operation=RevisionOperation.REPLACE_MEETING_TIME,
            section_id="section-1",
            weekday=2,
            start_time=time(9, 30),
            end_time=time(10, 30),
        )
    )

    assert instructor.revised_option.selected_sections[0].section_id == "section-2"
    assert delivery.revised_option.selected_sections[0].section_id == "section-2"
    assert meeting.revised_option.selected_sections[0].section_id == "section-2"


def test_revision_engine_reports_conflicts_after_revision():
    service = _service_with_session()

    result = service.revise(
        ScheduleRevisionRequest(
            session_id="session-1",
            option_id="option-1",
            operation=RevisionOperation.REPLACE_SECTION,
            section_id="section-1",
            replacement_section_id="section-2",
        )
    )

    assert result.revised_option.conflicts
    assert result.revised_option.metrics is not None
    assert result.revised_option.metrics.total_sections == 2


def test_revision_engine_undo_redo_and_restore_original():
    service = _service_with_session()
    service.revise(
        ScheduleRevisionRequest(
            session_id="session-1",
            option_id="option-1",
            operation=RevisionOperation.REPLACE_SECTION,
            section_id="section-1",
            replacement_section_id="section-2",
        )
    )

    undone = service.undo_last_revision(SessionIdRequest(session_id="session-1"))
    undone_section_id = undone.session.state.generated.options[0].selected_sections[0].section_id
    redone = service.redo_last_revision(SessionIdRequest(session_id="session-1"))
    redone_section_id = redone.session.state.generated.options[0].selected_sections[0].section_id
    restored = service.restore_original(
        RestoreOriginalScheduleRequest(session_id="session-1")
    )

    assert undone_section_id == "section-1"
    assert redone_section_id == "section-2"
    assert restored.session.state.generated.options[0].selected_sections[0].section_id == "section-1"
    assert restored.session.state.revision_count == 0


def test_revision_engine_applies_and_removes_temporary_preferences():
    service = _service_with_session()

    applied = service.revise(
        ScheduleRevisionRequest(
            session_id="session-1",
            option_id="option-1",
            operation=RevisionOperation.APPLY_TEMPORARY_PREFERENCE,
            preference={"key": "avoid_friday", "value": True},
        )
    )
    removed = service.revise(
        ScheduleRevisionRequest(
            session_id="session-1",
            option_id="option-1",
            operation=RevisionOperation.REMOVE_TEMPORARY_PREFERENCE,
            preference={"key": "avoid_friday"},
        )
    )

    assert applied.revision.operation == RevisionOperation.APPLY_TEMPORARY_PREFERENCE
    assert removed.revision.operation == RevisionOperation.REMOVE_TEMPORARY_PREFERENCE
    assert removed.revision is not None
    assert removed.success is True


def _service_with_session() -> ScheduleRevisionService:
    session_service = SchedulingSessionService()
    session = _session()
    session_service._sessions[session.state.session_id] = session
    return ScheduleRevisionService(session_service=session_service)


def _session() -> SchedulingSession:
    original = _option(
        "option-1",
        [_section("section-1", "course-1", "001", "Dr. Early", "In Person")],
        [_meeting("meeting-1", "section-1", 1, time(9, 0), time(10, 0))],
    )
    original = original.model_copy(
        update={
            "selected_sections": original.selected_sections
            + [_section("section-3", "course-2", "001", "Dr. Core", "In Person")],
            "selected_meetings": original.selected_meetings
            + [_meeting("meeting-3", "section-3", 2, time(9, 45), time(10, 45))],
        },
        deep=True,
    )
    alternative = _option(
        "option-2",
        [_section("section-2", "course-1", "002", "Dr. Later", "Online")],
        [_meeting("meeting-2", "section-2", 2, time(9, 30), time(10, 30))],
    )
    generated = GeneratedScheduleSet(
        options=[original, alternative],
        ranking_order=["option-1", "option-2"],
        generation_metadata={"generated_count": 2},
        generated_at=datetime(2026, 6, 1, 9, 0),
    )
    return SchedulingSession(
        state=SessionState(
            session_id="session-1",
            user_id=1,
            lifecycle=SessionLifecycle.ACTIVE,
            current_plan_id="plan-1",
            current_term_id="term-1",
            generated=generated,
            original_generated=generated.model_copy(deep=True),
            created_at=datetime(2026, 6, 1, 9, 0),
            updated_at=datetime(2026, 6, 1, 9, 0),
        )
    )


def _option(option_id: str, sections: list[ScheduleSection], meetings: list[ScheduleMeeting]):
    return ScheduleOption(
        option_id=option_id,
        rank=1,
        score=70,
        normalized_score=70,
        selected_sections=sections,
        selected_meetings=meetings,
        explanation="Option.",
    )


def _section(
    section_id: str,
    course_id: str,
    section_number: str,
    instructor: str,
    instruction_method: str,
) -> ScheduleSection:
    return ScheduleSection(
        section_id=section_id,
        offering_id=f"offering-{course_id}",
        course_id=course_id,
        term_id="term-1",
        offering_type="Lecture",
        section_number=section_number,
        crn=f"crn-{section_id}",
        instructor=instructor,
        instruction_method=instruction_method,
        capacity=20,
        enrolled=5,
        available_seats=15,
        status="Open",
    )


def _meeting(
    meeting_id: str,
    section_id: str,
    weekday: int,
    start_time: time,
    end_time: time,
) -> ScheduleMeeting:
    return ScheduleMeeting(
        meeting_id=meeting_id,
        section_id=section_id,
        weekday=weekday,
        start_time=start_time,
        end_time=end_time,
        meeting_type="Class",
        is_async=False,
    )
