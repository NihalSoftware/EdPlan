from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.orchestrator.execution.module_executor import ModuleExecutionResult
from app.orchestrator.schemas.intent_result import IntentResult
from app.orchestrator.schemas.module_response import FinalResponse
from app.orchestrator.schemas.student_context import StudentContext
from app.orchestrator.schemas.workflow_event import WorkflowEvent


class EdPlanState(BaseModel):
    """Central state object passed through the student orchestration workflow."""

    user_id: int = Field(..., gt=0)
    plan_id: UUID
    query: str = Field(..., min_length=1)
    student_context: StudentContext | None = None
    intent_result: IntentResult | None = None
    selected_modules: list[str] = Field(default_factory=list)
    module_results: dict[str, ModuleExecutionResult] = Field(default_factory=dict)
    workflow_events: list[WorkflowEvent] = Field(default_factory=list)
    final_response: FinalResponse | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
