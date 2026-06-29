from __future__ import annotations

import uuid
from datetime import datetime, time

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.db.session import get_db
from app.orchestrator.schemas.module_response import ModuleResponse
from app.student.domains.scheduling.api import schedulepilot
from app.student.domains.scheduling.engine import ScheduleMetrics, ScheduleOption
from app.student.domains.scheduling.schemas.schedule_persistence import (
    ActivationResult,
    SaveScheduleResult,
    SavedScheduleDetail,
    SavedScheduleSectionDetail,
    ScheduleSummary,
)
from app.student.domains.scheduling.schemas.revision import (
    RevisionOperation,
    RevisionSummary,
    ScheduleRevisionResult,
)
from app.student.domains.scheduling.schemas.session import (
    GeneratedScheduleSet,
    SchedulingSession,
    SessionLifecycle,
    SessionOperationResult,
    SessionState,
)
from app.student.domains.scheduling.schemas.schedulepilot import ScheduleMeeting, ScheduleSection


class _FakeSchedulePilotModule:
    def __init__(self, db=None):
        self.db = db

    async def execute(self, context, query):
        option = _option()
        return ModuleResponse(
            module_name="scheduling",
            content="Generated.",
            data={
                "ranked_options": [option.model_dump(mode="json")],
                "top_option": option.model_dump(mode="json"),
                "metrics_metadata": {"computed": 1},
            },
            confidence=0.75,
            metadata={
                "status": "ok",
                "next_action": "show_results",
                "reason": "generation_complete",
                "query": query,
                "counts": {"ranked_options": 1},
                "user_id": context.user["id"],
            },
        )


class _FakePersistenceService:
    def __init__(self):
        self.detail = _detail()

    async def save_schedule(self, db, request):
        self.detail = _detail(
            schedule_id="saved-schedule-1",
            plan_id=request.plan_id,
            schedule_name=request.schedule_name,
        )
        return SaveScheduleResult(
            success=True,
            schedule=_summary(
                schedule_id=self.detail.schedule_id,
                plan_id=request.plan_id,
                schedule_name=request.schedule_name,
            ),
        )

    async def get_saved_schedule(self, db, *, user_id, plan_id, schedule_id):
        return _detail(schedule_id=schedule_id, plan_id=plan_id)

    async def list_plan_schedules(self, db, *, user_id, plan_id):
        return [
            _summary(schedule_id="schedule-1", plan_id=plan_id),
            _summary(schedule_id="schedule-2", plan_id=plan_id),
        ]

    async def activate_schedule(self, db, request):
        return ActivationResult(
            success=True,
            activated_schedule=_summary(
                schedule_id=request.schedule_id,
                plan_id=request.plan_id,
                status="Active",
                is_active=True,
            ),
            deactivated_schedule_ids=["previous-schedule"],
        )

    async def archive_schedule(self, db, request):
        return _summary(
            schedule_id=request.schedule_id,
            plan_id=request.plan_id,
            status="Archived",
            is_active=False,
        )


class _FakeSessionService:
    def __init__(self):
        self.session = _session()

    async def start_session(self, db, request):
        return SessionOperationResult(
            success=True,
            session=self.session,
            message="Scheduling session started.",
        )

    def load_session(self, request):
        return SessionOperationResult(
            success=True,
            session=self.session,
            message="Scheduling session loaded.",
        )

    def select_option(self, request):
        self.session.state.selection.selected_option_id = request.option_id
        return SessionOperationResult(
            success=True,
            session=self.session,
            message="Schedule option selected.",
        )

    def compare_options(self, request):
        self.session.state.comparison.option_ids = list(request.option_ids)
        return SessionOperationResult(
            success=True,
            session=self.session,
            message="Schedule options compared.",
        )

    async def regenerate(self, db, request):
        return SessionOperationResult(
            success=True,
            session=self.session,
            message="Scheduling session regenerated.",
        )

    def undo_last_action(self, request):
        return SessionOperationResult(
            success=True,
            session=self.session,
            message="Last session action undone.",
        )

    def reset_session(self, request):
        self.session.state.generated = GeneratedScheduleSet()
        return SessionOperationResult(
            success=True,
            session=self.session,
            message="Scheduling session reset.",
        )

    def close_session(self, request):
        self.session.state.lifecycle = SessionLifecycle.CLOSED
        return SessionOperationResult(
            success=True,
            session=self.session,
            message="Scheduling session closed.",
        )


class _FakeRevisionService:
    def __init__(self):
        self.session = _session()

    def revise(self, request):
        return ScheduleRevisionResult(
            success=True,
            session_id=request.session_id,
            revised_option=_option(),
            revision=RevisionSummary(
                revision_id="revision-1",
                operation=request.operation,
                option_id=request.option_id or "option-1",
                replaced_section_ids=["section-1"],
                added_section_ids=["section-2"],
                created_at=datetime(2026, 6, 1, 9, 0),
            ),
            message="Schedule revision applied.",
        )

    def lock_section(self, request):
        return SessionOperationResult(
            success=True,
            session=self.session,
            message="Locked schedule section.",
        )

    def unlock_section(self, request):
        return SessionOperationResult(
            success=True,
            session=self.session,
            message="Unlocked schedule section.",
        )

    def restore_original(self, request):
        return SessionOperationResult(
            success=True,
            session=self.session,
            message="Restored original generated schedule set.",
        )

    def undo_last_revision(self, request):
        return SessionOperationResult(
            success=True,
            session=self.session,
            message="Undid schedule revision.",
        )

    def redo_last_revision(self, request):
        return SessionOperationResult(
            success=True,
            session=self.session,
            message="Redid schedule revision.",
        )


@pytest.fixture()
def client(monkeypatch):
    app = FastAPI()
    app.include_router(schedulepilot.router, prefix="/api")

    async def override_db():
        yield object()

    service = _FakePersistenceService()
    session_service = _FakeSessionService()
    revision_service = _FakeRevisionService()
    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[
        schedulepilot.get_schedule_persistence_service
    ] = lambda: service
    app.dependency_overrides[
        schedulepilot.get_scheduling_session_service
    ] = lambda: session_service
    app.dependency_overrides[
        schedulepilot.get_schedule_revision_service
    ] = lambda: revision_service
    monkeypatch.setattr(schedulepilot, "SchedulePilotModule", _FakeSchedulePilotModule)
    return TestClient(app)


def test_generate_schedule_returns_ranked_options_without_persisting(client):
    response = client.post(
        "/api/schedulepilot/generate",
        json={
            "user_id": 1,
            "plan_id": str(uuid.uuid4()),
            "preferences": [{"key": "morning_classes", "value": True}],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["metadata"]["status"] == "ok"
    assert len(body["data"]["ranked_options"]) == 1


def test_save_schedule_persists_selected_option_and_returns_detail(client):
    plan_id = str(uuid.uuid4())
    response = client.post(
        "/api/schedulepilot/schedules",
        json={
            "user_id": 1,
            "plan_id": plan_id,
            "selected_option": _option().model_dump(mode="json"),
            "schedule_name": "Best schedule",
            "confirmed": True,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["data"]["schedule_id"] == "saved-schedule-1"
    assert body["data"]["plan_id"] == plan_id


def test_list_saved_schedules_returns_plan_summaries(client):
    plan_id = str(uuid.uuid4())
    response = client.get(
        f"/api/schedulepilot/plans/{plan_id}/schedules",
        params={"user_id": 1},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["metadata"]["count"] == 2
    assert [item["schedule_id"] for item in body["data"]] == ["schedule-1", "schedule-2"]


def test_get_saved_schedule_returns_full_detail(client):
    plan_id = str(uuid.uuid4())
    response = client.get(
        "/api/schedulepilot/schedules/schedule-1",
        params={"user_id": 1, "plan_id": plan_id},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["metrics_snapshot"]["total_credits"] == 3
    assert body["data"]["selected_sections"][0]["meeting_snapshot"][0]["meeting_id"] == "m1"


def test_activate_schedule_uses_activation_workflow(client):
    plan_id = str(uuid.uuid4())
    response = client.post(
        "/api/schedulepilot/schedules/schedule-1/activate",
        json={"user_id": 1, "plan_id": plan_id, "confirmed": True},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["activated_schedule"]["status"] == "Active"
    assert body["data"]["deactivated_schedule_ids"] == ["previous-schedule"]


def test_archive_schedule_uses_archive_workflow(client):
    plan_id = str(uuid.uuid4())
    response = client.post(
        "/api/schedulepilot/schedules/schedule-1/archive",
        json={"user_id": 1, "plan_id": plan_id, "confirmed": True},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "Archived"
    assert body["data"]["is_active"] is False


def test_compare_schedules_returns_snapshot_based_comparison(client):
    plan_id = str(uuid.uuid4())
    response = client.post(
        "/api/schedulepilot/compare",
        json={
            "user_id": 1,
            "plan_id": plan_id,
            "schedule_ids": ["schedule-1", "schedule-2"],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["metadata"]["count"] == 2
    assert body["data"][0]["metrics_snapshot"]["total_credits"] == 3
    assert body["data"][0]["selected_section_count"] == 1


def test_start_session_returns_session_state(client):
    response = client.post(
        "/api/schedulepilot/session/start",
        json={"user_id": 1, "plan_id": "plan-1"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["session"]["state"]["session_id"] == "session-1"


def test_load_session_returns_current_session(client):
    response = client.get("/api/schedulepilot/session", params={"session_id": "session-1"})

    assert response.status_code == 200
    assert response.json()["message"] == "Scheduling session loaded."


def test_select_session_option_updates_selection(client):
    response = client.post(
        "/api/schedulepilot/session/select",
        json={"session_id": "session-1", "option_id": "option-1"},
    )

    assert response.status_code == 200
    assert response.json()["session"]["state"]["selection"]["selected_option_id"] == "option-1"


def test_compare_session_options_updates_comparison(client):
    response = client.post(
        "/api/schedulepilot/session/compare",
        json={"session_id": "session-1", "option_ids": ["option-1", "option-2"]},
    )

    assert response.status_code == 200
    assert response.json()["session"]["state"]["comparison"]["option_ids"] == [
        "option-1",
        "option-2",
    ]


def test_regenerate_undo_reset_and_close_session(client):
    regenerate = client.post(
        "/api/schedulepilot/session/regenerate",
        json={"session_id": "session-1", "preferences": [{"key": "time", "value": "morning"}]},
    )
    undo = client.post("/api/schedulepilot/session/undo", json={"session_id": "session-1"})
    reset = client.post("/api/schedulepilot/session/reset", json={"session_id": "session-1"})
    close = client.post("/api/schedulepilot/session/close", json={"session_id": "session-1"})

    assert regenerate.status_code == 200
    assert undo.status_code == 200
    assert reset.status_code == 200
    assert reset.json()["session"]["state"]["generated"]["options"] == []
    assert close.status_code == 200
    assert close.json()["session"]["state"]["lifecycle"] == "closed"


def test_revision_endpoints_use_revision_service(client):
    revise = client.post(
        "/api/schedulepilot/session/revise",
        json={
            "session_id": "session-1",
            "operation": RevisionOperation.REPLACE_SECTION,
            "option_id": "option-1",
            "section_id": "section-1",
            "replacement_section_id": "section-2",
        },
    )
    lock = client.post(
        "/api/schedulepilot/session/lock",
        json={"session_id": "session-1", "section_id": "section-1"},
    )
    unlock = client.post(
        "/api/schedulepilot/session/unlock",
        json={"session_id": "session-1", "section_id": "section-1"},
    )
    restore = client.post(
        "/api/schedulepilot/session/restore",
        json={"session_id": "session-1"},
    )
    undo = client.post(
        "/api/schedulepilot/session/revision/undo",
        json={"session_id": "session-1"},
    )
    redo = client.post(
        "/api/schedulepilot/session/revision/redo",
        json={"session_id": "session-1"},
    )

    assert revise.status_code == 200
    assert revise.json()["revision"]["operation"] == "replace_section"
    assert lock.status_code == 200
    assert unlock.status_code == 200
    assert restore.status_code == 200
    assert undo.status_code == 200
    assert redo.status_code == 200


def _option() -> ScheduleOption:
    section_id = str(uuid.uuid4())
    return ScheduleOption(
        option_id="option-1",
        rank=1,
        score=90,
        normalized_score=90,
        selected_sections=[
            ScheduleSection(
                section_id=section_id,
                offering_id=str(uuid.uuid4()),
                course_id=str(uuid.uuid4()),
                term_id=str(uuid.uuid4()),
                offering_type="Lecture",
                section_number="001",
                crn="12345",
                instruction_method="In Person",
                capacity=30,
                enrolled=12,
                available_seats=18,
                status="Open",
            )
        ],
        selected_meetings=[
            ScheduleMeeting(
                meeting_id="m1",
                section_id=section_id,
                weekday=1,
                start_time=time(9, 0),
                end_time=time(10, 0),
                meeting_type="Class",
                is_async=False,
            )
        ],
        metrics=ScheduleMetrics(
            total_credits=3,
            earliest_start_time=time(9, 0),
            latest_end_time=time(10, 0),
            total_instruction_minutes=60,
            total_gap_minutes=0,
            average_gap_minutes=0,
            maximum_gap_minutes=0,
            campus_days=1,
            monday_classes=1,
            tuesday_classes=0,
            wednesday_classes=0,
            thursday_classes=0,
            friday_classes=0,
            saturday_classes=0,
            sunday_classes=0,
            online_section_count=0,
            hybrid_section_count=0,
            in_person_section_count=1,
            asynchronous_section_count=0,
            total_sections=1,
            open_sections=1,
            closed_sections=0,
            cancelled_sections=0,
            available_seat_count=18,
            total_capacity=30,
            total_enrollment=12,
            open_seat_ratio=0.6,
            total_meetings=1,
            synchronous_meetings=1,
            asynchronous_meetings=0,
            average_meeting_duration=60,
            longest_meeting_duration=60,
            total_courses=1,
            lecture_count=1,
            lab_count=0,
            discussion_count=0,
            other_component_count=0,
        ),
        warnings=[],
        conflicts=[],
        explanation="Best rule-based option.",
        tradeoffs=["Morning schedule"],
    )


def _summary(
    *,
    schedule_id: str,
    plan_id: str,
    schedule_name: str | None = "Best schedule",
    status: str = "Final",
    is_active: bool = False,
) -> ScheduleSummary:
    return ScheduleSummary(
        schedule_id=schedule_id,
        plan_id=plan_id,
        schedule_name=schedule_name,
        status=status,
        is_active=is_active,
        is_favorite=False,
        total_credits=3,
        generated_at=datetime(2026, 6, 1, 9, 0),
        selected_section_ids=["section-1"],
    )


def _detail(
    *,
    schedule_id: str = "schedule-1",
    plan_id: str | None = None,
    schedule_name: str | None = "Best schedule",
) -> SavedScheduleDetail:
    section_detail = SavedScheduleSectionDetail(
        id="row-1",
        schedule_id=schedule_id,
        section_id="section-1",
        display_order=0,
        course_id_snapshot="course-1",
        section_number_snapshot="001",
        crn_snapshot="12345",
        instruction_method_snapshot="In Person",
        meeting_snapshot=[{"meeting_id": "m1", "section_id": "section-1"}],
        created_at=datetime(2026, 6, 1, 9, 0),
    )
    return SavedScheduleDetail(
        schedule_id=schedule_id,
        plan_id=plan_id or str(uuid.uuid4()),
        selected_term_id=str(uuid.uuid4()),
        schedule_name=schedule_name,
        status="Final",
        source="user_created",
        is_active=False,
        is_favorite=False,
        total_credits=3,
        score=90,
        normalized_score=90,
        rank_at_generation=1,
        metrics_snapshot={"total_credits": 3},
        conflicts_snapshot=[],
        warnings_snapshot=[],
        tradeoffs_snapshot=["Morning schedule"],
        explanation_snapshot={"content": "Best rule-based option."},
        generation_metadata={"source_option_id": "option-1"},
        selected_sections=[section_detail],
        selected_section_ids=["section-1"],
        created_at=datetime(2026, 6, 1, 9, 0),
        updated_at=datetime(2026, 6, 1, 9, 0),
    )


def _session() -> SchedulingSession:
    return SchedulingSession(
        state=SessionState(
            session_id="session-1",
            user_id=1,
            lifecycle=SessionLifecycle.ACTIVE,
            current_plan_id="plan-1",
            current_term_id="term-1",
            generated=GeneratedScheduleSet(
                options=[_option()],
                ranking_order=["option-1"],
                generation_metadata={"generated_count": 1},
                generated_at=datetime(2026, 6, 1, 9, 0),
            ),
            created_at=datetime(2026, 6, 1, 9, 0),
            updated_at=datetime(2026, 6, 1, 9, 0),
        )
    )
