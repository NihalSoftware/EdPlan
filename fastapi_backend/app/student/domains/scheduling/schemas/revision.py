from __future__ import annotations

from datetime import datetime, time
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from app.student.domains.scheduling.engine import ScheduleOption


class RevisionOperation(StrEnum):
    REPLACE_SECTION = "replace_section"
    REPLACE_INSTRUCTOR = "replace_instructor"
    REPLACE_MEETING_TIME = "replace_meeting_time"
    REPLACE_DELIVERY = "replace_delivery"
    KEEP_SELECTED_FIXED = "keep_selected_fixed"
    APPLY_TEMPORARY_PREFERENCE = "apply_temporary_preference"
    REMOVE_TEMPORARY_PREFERENCE = "remove_temporary_preference"


class LockedSection(BaseModel):
    section_id: str
    course_id: str | None = None
    reason: str | None = None
    locked_at: datetime


class RevisionSummary(BaseModel):
    revision_id: str
    operation: RevisionOperation
    option_id: str
    affected_course_ids: list[str] = Field(default_factory=list)
    replaced_section_ids: list[str] = Field(default_factory=list)
    added_section_ids: list[str] = Field(default_factory=list)
    locked_section_ids: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    created_at: datetime


class RevisionHistory(BaseModel):
    revisions: list[RevisionSummary] = Field(default_factory=list)
    redo_stack: list[dict[str, Any]] = Field(default_factory=list)


class ScheduleRevisionRequest(BaseModel):
    session_id: str
    operation: RevisionOperation
    option_id: str | None = None
    course_id: str | None = None
    section_id: str | None = None
    replacement_section_id: str | None = None
    instructor: str | None = None
    weekday: int | None = None
    start_time: time | None = None
    end_time: time | None = None
    instruction_method: str | None = None
    preference: dict[str, Any] | None = None


class LockSectionRequest(BaseModel):
    session_id: str
    section_id: str
    course_id: str | None = None
    reason: str | None = None


class UnlockSectionRequest(BaseModel):
    session_id: str
    section_id: str


class RestoreOriginalScheduleRequest(BaseModel):
    session_id: str


class ScheduleRevisionResult(BaseModel):
    success: bool
    session_id: str
    revised_option: ScheduleOption | None = None
    revision: RevisionSummary | None = None
    message: str
