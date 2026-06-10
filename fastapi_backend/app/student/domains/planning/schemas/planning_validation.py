from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from app.student.domains.planning.schemas.normalized_plan import PlanCourseStatus

ValidationSeverity = Literal["error", "warning", "recommendation"]
PlanValidationMode = Literal["save", "draft"]
PlanCourseValidationOperation = Literal["add", "update", "move"]


class PlanValidationRequest(BaseModel):
    mode: PlanValidationMode = "save"


class PlanCourseValidationRequest(BaseModel):
    course_id: str = Field(min_length=1)
    planned_term_id: str | None = None
    status: PlanCourseStatus = "Planned"
    operation: PlanCourseValidationOperation = "add"


class ValidationIssue(BaseModel):
    severity: ValidationSeverity
    code: str
    message: str
    plan_course_id: str | None = None
    course_id: str | None = None
    course_code: str | None = None
    planned_term_id: str | None = None
    planned_term_name: str | None = None
    related_course_ids: list[str] = Field(default_factory=list)
    related_course_codes: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ValidationSummary(BaseModel):
    error_count: int
    warning_count: int
    recommendation_count: int


class PlanValidationResult(BaseModel):
    plan_id: str
    is_valid: bool
    issues: list[ValidationIssue] = Field(default_factory=list)
    summary: ValidationSummary


class PlanValidationResponse(BaseModel):
    success: bool
    data: PlanValidationResult
