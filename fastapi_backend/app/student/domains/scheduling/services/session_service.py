from __future__ import annotations

import uuid
from copy import deepcopy
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.student.domains.scheduling.schemas.decision import (
    DecisionStatus,
    ScheduleDecisionRequest,
    ScheduleDecisionResult,
)
from app.student.domains.scheduling.schemas.session import (
    CompareOptionsRequest,
    GeneratedScheduleSet,
    RegenerateSessionRequest,
    SelectOptionRequest,
    SessionComparison,
    SessionHistoryAction,
    SessionHistoryEntry,
    SessionIdRequest,
    SessionLifecycle,
    SessionOperationResult,
    SessionPreferences,
    SessionSelection,
    SessionState,
    SchedulingSession,
    StartSessionRequest,
    TemporaryPreference,
)
from app.student.domains.scheduling.services.decision_service import (
    ScheduleDecisionService,
    schedule_decision_service,
)


class SchedulingSessionService:
    """In-memory deterministic working memory for SchedulePilot interactions."""

    def __init__(self, decision_service: ScheduleDecisionService | None = None) -> None:
        self.decision_service = decision_service or schedule_decision_service
        self._sessions: dict[str, SchedulingSession] = {}

    async def start_session(
        self,
        db: AsyncSession,
        request: StartSessionRequest,
    ) -> SessionOperationResult:
        session = self.create_session(request)
        session_id = session.state.session_id
        decision = await self.decision_service.decide_and_generate(
            db,
            ScheduleDecisionRequest(
                user_id=request.user_id,
                plan_id=request.plan_id,
                term_id=request.term_id,
                query=request.query,
                preferences=[preference.model_dump(mode="json") for preference in request.preferences],
            ),
        )
        self.apply_decision(session_id, decision, history_action=SessionHistoryAction.GENERATED)
        return SessionOperationResult(
            success=True,
            session=self._require_session(session_id),
            message="Scheduling session started.",
        )

    def create_session(self, request: StartSessionRequest) -> SchedulingSession:
        now = _utcnow()
        session_id = str(uuid.uuid4())
        session = SchedulingSession(
            state=SessionState(
                session_id=session_id,
                user_id=request.user_id,
                lifecycle=SessionLifecycle.CREATED,
                current_plan_id=request.plan_id,
                current_term_id=request.term_id,
                preferences=SessionPreferences(temporary=list(request.preferences)),
                created_at=now,
                updated_at=now,
            )
        )
        _append_history(
            session,
            SessionHistoryAction.CREATED,
            "Scheduling session created.",
        )
        self._sessions[session_id] = session
        return session

    def load_session(self, request: SessionIdRequest) -> SessionOperationResult:
        session = self._require_session(request.session_id)
        return SessionOperationResult(
            success=True,
            session=session,
            message="Scheduling session loaded.",
        )

    def apply_decision(
        self,
        session_id: str,
        decision: ScheduleDecisionResult,
        *,
        history_action: SessionHistoryAction = SessionHistoryAction.GENERATED,
    ) -> SchedulingSession:
        session = self._require_session(session_id)
        previous_state = _history_snapshot(session)
        state = session.state
        state.current_plan_id = decision.context.resolved_plan_id or state.current_plan_id
        state.current_term_id = decision.context.resolved_term_id or state.current_term_id
        state.current_next_action = decision.next_action
        state.decision_status = decision.status
        state.warnings = list(decision.warnings)
        state.errors = list(decision.errors)
        if decision.ranking_result is not None:
            generated = GeneratedScheduleSet(
                options=list(decision.ranking_result.options),
                ranking_order=[
                    option.option_id for option in decision.ranking_result.options
                ],
                generation_metadata=decision.generation_metadata or {},
                ranking_metadata=decision.ranking_result.metadata.model_dump(mode="json"),
                generated_at=_utcnow(),
            )
            state.generated = generated
            if state.original_generated is None:
                state.original_generated = generated.model_copy(deep=True)
        state.lifecycle = _lifecycle_for_decision(decision.status)
        state.updated_at = _utcnow()
        _append_history(
            session,
            history_action,
            _history_description(history_action, decision.status),
            previous_state=previous_state,
        )
        return session

    def select_option(self, request: SelectOptionRequest) -> SessionOperationResult:
        session = self._require_session(request.session_id)
        if request.option_id not in session.state.generated.ranking_order:
            raise ValueError("Schedule option is not available in the current session.")
        previous_state = _history_snapshot(session)
        now = _utcnow()
        session.state.selection = SessionSelection(
            selected_option_id=request.option_id,
            selected_schedule_id=request.selected_schedule_id,
            selected_at=now,
        )
        session.state.lifecycle = SessionLifecycle.ACTIVE
        session.state.updated_at = now
        _append_history(
            session,
            SessionHistoryAction.SELECTED_OPTION,
            f"Selected schedule option {request.option_id}.",
            previous_state=previous_state,
        )
        return SessionOperationResult(
            success=True,
            session=session,
            message="Schedule option selected.",
        )

    def compare_options(self, request: CompareOptionsRequest) -> SessionOperationResult:
        session = self._require_session(request.session_id)
        missing_options = [
            option_id
            for option_id in request.option_ids
            if option_id not in session.state.generated.ranking_order
        ]
        if missing_options:
            raise ValueError(
                "Schedule options are not available in the current session: "
                + ", ".join(missing_options)
            )
        previous_state = _history_snapshot(session)
        session.state.comparison = SessionComparison(
            option_ids=list(request.option_ids),
            compared_at=_utcnow(),
        )
        session.state.updated_at = _utcnow()
        _append_history(
            session,
            SessionHistoryAction.COMPARED_OPTIONS,
            "Compared schedule options.",
            previous_state=previous_state,
        )
        return SessionOperationResult(
            success=True,
            session=session,
            message="Schedule options compared.",
        )

    async def regenerate(
        self,
        db: AsyncSession,
        request: RegenerateSessionRequest,
    ) -> SessionOperationResult:
        session = self._require_session(request.session_id)
        if session.state.lifecycle == SessionLifecycle.CLOSED:
            raise ValueError("Closed scheduling sessions cannot be regenerated.")
        if request.preferences:
            session.state.preferences.temporary = _merge_temporary_preferences(
                session.state.preferences.temporary,
                request.preferences,
            )
        decision = await self.decision_service.decide_and_generate(
            db,
            ScheduleDecisionRequest(
                user_id=session.state.user_id,
                plan_id=request.plan_id or session.state.current_plan_id,
                term_id=request.term_id or session.state.current_term_id,
                query=request.query,
                preferences=[
                    preference.model_dump(mode="json")
                    for preference in session.state.preferences.temporary
                ],
            ),
        )
        self.apply_decision(
            request.session_id,
            decision,
            history_action=SessionHistoryAction.REGENERATED,
        )
        return SessionOperationResult(
            success=True,
            session=self._require_session(request.session_id),
            message="Scheduling session regenerated.",
        )

    def undo_last_action(self, request: SessionIdRequest) -> SessionOperationResult:
        session = self._require_session(request.session_id)
        restorable = [
            entry for entry in session.state.history if entry.previous_state is not None
        ]
        if not restorable:
            raise ValueError("No session action can be undone.")
        snapshot = restorable[-1].previous_state
        history = list(session.state.history)
        restored_state = SessionState.model_validate(snapshot)
        restored_state.history = history
        restored_state.updated_at = _utcnow()
        session.state = restored_state
        _append_history(
            session,
            SessionHistoryAction.UNDONE,
            "Undid the last session action.",
        )
        return SessionOperationResult(
            success=True,
            session=session,
            message="Last session action undone.",
        )

    def reset_session(self, request: SessionIdRequest) -> SessionOperationResult:
        session = self._require_session(request.session_id)
        previous_state = _history_snapshot(session)
        now = _utcnow()
        session.state.generated = GeneratedScheduleSet()
        session.state.selection = SessionSelection()
        session.state.comparison = SessionComparison()
        session.state.current_next_action = None
        session.state.decision_status = None
        session.state.warnings = []
        session.state.errors = []
        session.state.lifecycle = SessionLifecycle.CREATED
        session.state.updated_at = now
        _append_history(
            session,
            SessionHistoryAction.RESET,
            "Scheduling session reset.",
            previous_state=previous_state,
        )
        return SessionOperationResult(
            success=True,
            session=session,
            message="Scheduling session reset.",
        )

    def close_session(self, request: SessionIdRequest) -> SessionOperationResult:
        session = self._require_session(request.session_id)
        previous_state = _history_snapshot(session)
        now = _utcnow()
        session.state.lifecycle = SessionLifecycle.CLOSED
        session.state.closed_at = now
        session.state.updated_at = now
        _append_history(
            session,
            SessionHistoryAction.CLOSED,
            "Scheduling session closed.",
            previous_state=previous_state,
        )
        return SessionOperationResult(
            success=True,
            session=session,
            message="Scheduling session closed.",
        )

    def _require_session(self, session_id: str) -> SchedulingSession:
        try:
            return self._sessions[session_id]
        except KeyError as exc:
            raise ValueError("Scheduling session not found.") from exc

    def get_session(self, session_id: str) -> SchedulingSession:
        return self._require_session(session_id)


def _lifecycle_for_decision(status: DecisionStatus) -> SessionLifecycle:
    if status == DecisionStatus.NEEDS_INPUT:
        return SessionLifecycle.WAITING_FOR_INPUT
    if status in {DecisionStatus.OK, DecisionStatus.WARNING, DecisionStatus.PARTIAL}:
        return SessionLifecycle.ACTIVE
    return SessionLifecycle.COMPLETED


def _append_history(
    session: SchedulingSession,
    action: SessionHistoryAction,
    description: str,
    *,
    previous_state: dict | None = None,
) -> None:
    session.state.history.append(
        SessionHistoryEntry(
            action=action,
            created_at=_utcnow(),
            description=description,
            previous_state=previous_state,
        )
    )


def _history_snapshot(session: SchedulingSession) -> dict:
    return deepcopy(
        session.state.model_dump(
            mode="json",
            exclude={"history"},
        )
        | {"history": [entry.model_dump(mode="json") for entry in session.state.history]}
    )


def _history_description(action: SessionHistoryAction, status: DecisionStatus) -> str:
    if action == SessionHistoryAction.REGENERATED:
        return f"Regenerated schedule options with decision status {status}."
    return f"Generated schedule options with decision status {status}."


def _merge_temporary_preferences(
    existing: list[TemporaryPreference],
    incoming: list[TemporaryPreference],
) -> list[TemporaryPreference]:
    merged = {preference.key: preference for preference in existing}
    for preference in incoming:
        merged[preference.key] = preference
    return list(merged.values())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


scheduling_session_service = SchedulingSessionService()
