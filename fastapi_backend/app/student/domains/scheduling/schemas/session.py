from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from app.student.domains.scheduling.engine import ScheduleOption
from app.student.domains.scheduling.schemas.decision import DecisionNextAction, DecisionStatus
from app.student.domains.scheduling.schemas.revision import (
    LockedSection,
    RevisionSummary,
)


class SessionLifecycle(StrEnum):
    CREATED = "created"
    ACTIVE = "active"
    WAITING_FOR_INPUT = "waiting_for_input"
    COMPLETED = "completed"
    CLOSED = "closed"
    EXPIRED = "expired"


class SessionHistoryAction(StrEnum):
    CREATED = "created"
    GENERATED = "generated"
    SELECTED_OPTION = "selected_option"
    COMPARED_OPTIONS = "compared_options"
    REGENERATED = "regenerated"
    UNDONE = "undone"
    RESET = "reset"
    CLOSED = "closed"


class TemporaryPreference(BaseModel):
    key: str
    value: Any = None
    source: str = "session"


class SessionPreferences(BaseModel):
    temporary: list[TemporaryPreference] = Field(default_factory=list)


class SessionSelection(BaseModel):
    selected_option_id: str | None = None
    selected_schedule_id: str | None = None
    selected_at: datetime | None = None


class SessionComparison(BaseModel):
    option_ids: list[str] = Field(default_factory=list)
    schedule_ids: list[str] = Field(default_factory=list)
    compared_at: datetime | None = None


class GeneratedScheduleSet(BaseModel):
    options: list[ScheduleOption] = Field(default_factory=list)
    ranking_order: list[str] = Field(default_factory=list)
    generation_metadata: dict[str, Any] = Field(default_factory=dict)
    ranking_metadata: dict[str, Any] = Field(default_factory=dict)
    generated_at: datetime | None = None


class SessionHistoryEntry(BaseModel):
    action: SessionHistoryAction
    created_at: datetime
    description: str
    previous_state: dict[str, Any] | None = None


class SessionState(BaseModel):
    session_id: str
    user_id: int
    lifecycle: SessionLifecycle
    current_plan_id: str | None = None
    current_term_id: str | None = None
    generated: GeneratedScheduleSet = Field(default_factory=GeneratedScheduleSet)
    original_generated: GeneratedScheduleSet | None = None
    selection: SessionSelection = Field(default_factory=SessionSelection)
    comparison: SessionComparison = Field(default_factory=SessionComparison)
    preferences: SessionPreferences = Field(default_factory=SessionPreferences)
    locked_sections: list[LockedSection] = Field(default_factory=list)
    revision_history: list[RevisionSummary] = Field(default_factory=list)
    redo_stack: list[dict[str, Any]] = Field(default_factory=list)
    last_revision: RevisionSummary | None = None
    revision_count: int = 0
    history: list[SessionHistoryEntry] = Field(default_factory=list)
    current_next_action: DecisionNextAction | None = None
    decision_status: DecisionStatus | None = None
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None = None


class SchedulingSession(BaseModel):
    state: SessionState


class SessionOperationResult(BaseModel):
    success: bool
    session: SchedulingSession
    message: str


class StartSessionRequest(BaseModel):
    user_id: int
    plan_id: str | None = None
    term_id: str | None = None
    query: str | None = None
    preferences: list[TemporaryPreference] = Field(default_factory=list)


class LoadSessionRequest(BaseModel):
    session_id: str


class SelectOptionRequest(BaseModel):
    session_id: str
    option_id: str
    selected_schedule_id: str | None = None


class CompareOptionsRequest(BaseModel):
    session_id: str
    option_ids: list[str] = Field(min_length=2)


class RegenerateSessionRequest(BaseModel):
    session_id: str
    plan_id: str | None = None
    term_id: str | None = None
    query: str | None = None
    preferences: list[TemporaryPreference] = Field(default_factory=list)


class SessionIdRequest(BaseModel):
    session_id: str
