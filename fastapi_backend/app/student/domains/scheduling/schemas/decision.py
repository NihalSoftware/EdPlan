from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from app.student.domains.scheduling.engine import ScheduleRankingResult
from app.student.domains.scheduling.schemas.schedulepilot import ScheduleRetrievalContext


class DecisionStatus(StrEnum):
    OK = "ok"
    NEEDS_INPUT = "needs_input"
    WARNING = "warning"
    FAILED = "failed"
    PARTIAL = "partial"


class DecisionReason(StrEnum):
    READY = "ready"
    SINGLE_PLAN_RESOLVED = "single_plan_resolved"
    NO_PLANS = "no_plans"
    MULTIPLE_PLANS = "multiple_plans"
    PLAN_NOT_FOUND = "plan_not_found"
    INACTIVE_PLAN = "inactive_plan"
    EMPTY_PLAN = "empty_plan"
    UNKNOWN_TERM = "unknown_term"
    MULTIPLE_POSSIBLE_TERMS = "multiple_possible_terms"
    NO_OFFERINGS = "no_offerings"
    NO_SECTIONS = "no_sections"
    MISSING_MEETINGS = "missing_meetings"
    PARTIAL_SCHEDULING_DATA = "partial_scheduling_data"
    GENERATION_COMPLETE = "generation_complete"


class DecisionNextAction(StrEnum):
    GENERATE = "generate"
    ASK_FOR_PLAN = "ask_for_plan"
    ASK_FOR_TERM = "ask_for_term"
    REVIEW_WARNINGS = "review_warnings"
    SHOW_RESULTS = "show_results"
    STOP = "stop"


class ScheduleDecisionRequest(BaseModel):
    user_id: int
    plan_id: str | None = None
    term_id: str | None = None
    query: str | None = None
    preferences: list[dict[str, Any]] = Field(default_factory=list)
    saved_preferences: list[dict[str, Any]] = Field(default_factory=list)
    system_defaults: list[dict[str, Any]] = Field(default_factory=list)


class PlanDecisionOption(BaseModel):
    plan_id: str
    plan_name: str
    is_active: bool
    university_id: str | None = None
    program_id: str | None = None


class TermDecisionOption(BaseModel):
    term_id: str
    term_name: str
    is_active: bool


class DecisionContext(BaseModel):
    user_id: int
    resolved_plan_id: str | None = None
    resolved_term_id: str | None = None
    available_plans: list[PlanDecisionOption] = Field(default_factory=list)
    available_terms: list[TermDecisionOption] = Field(default_factory=list)
    normalized_preferences: list[dict[str, Any]] = Field(default_factory=list)


class ScheduleDecisionResult(BaseModel):
    status: DecisionStatus
    next_action: DecisionNextAction
    reason: DecisionReason
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    context: DecisionContext
    retrieval_context: ScheduleRetrievalContext | None = None
    generation_metadata: dict[str, Any] | None = None
    generation_warnings: list[str] = Field(default_factory=list)
    validation_metadata: dict[str, Any] | None = None
    metrics_metadata: dict[str, Any] | None = None
    scoring_metadata: dict[str, Any] | None = None
    ranking_result: ScheduleRankingResult | None = None
    scored_candidates: list[dict[str, Any]] = Field(default_factory=list)
    explanation: str | None = None
