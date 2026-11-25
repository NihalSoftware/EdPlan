from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.student.domains.scheduling.engine import ScheduleOption
from app.student.domains.scheduling.schemas.schedule_persistence import (
    ActivationResult,
    SavedScheduleDetail,
    ScheduleSummary,
)


class GenerateScheduleRequest(BaseModel):
    user_id: int
    plan_id: str
    preferences: list[dict[str, Any]] = Field(default_factory=list)
    query: str | None = None


class GenerateScheduleResponse(BaseModel):
    success: bool
    data: dict[str, Any]
    metadata: dict[str, Any] = Field(default_factory=dict)


class SaveScheduleApiRequest(BaseModel):
    user_id: int
    plan_id: str
    selected_option: ScheduleOption
    schedule_name: str | None = None
    notes: str | None = None
    confirmed: bool = False


class SavedScheduleDetailResponse(BaseModel):
    success: bool
    data: SavedScheduleDetail


class SavedScheduleListResponse(BaseModel):
    success: bool
    data: list[ScheduleSummary]
    metadata: dict[str, Any] = Field(default_factory=dict)


class ActivateScheduleRequest(BaseModel):
    user_id: int
    plan_id: str
    confirmed: bool = True


class ActivationResponse(BaseModel):
    success: bool
    data: ActivationResult


class ArchiveScheduleResponse(BaseModel):
    success: bool
    data: ScheduleSummary


class CompareSchedulesRequest(BaseModel):
    user_id: int
    plan_id: str
    schedule_ids: list[str] = Field(min_length=2)


class ScheduleComparisonItem(BaseModel):
    schedule_id: str
    schedule_name: str | None = None
    status: str
    is_active: bool
    is_favorite: bool
    total_credits: int
    score: float | None = None
    normalized_score: float | None = None
    rank_at_generation: int | None = None
    selected_term_id: str | None = None
    selected_section_count: int
    conflict_count: int
    warning_count: int
    metrics_snapshot: dict[str, Any]
    tradeoffs_snapshot: list[Any]
    explanation_snapshot: dict[str, Any]


class CompareSchedulesResponse(BaseModel):
    success: bool
    data: list[ScheduleComparisonItem]
    metadata: dict[str, Any] = Field(default_factory=dict)
