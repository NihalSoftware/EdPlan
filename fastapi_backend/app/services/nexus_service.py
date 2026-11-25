from __future__ import annotations

import logging
from time import perf_counter
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.orchestrator.schemas.module_response import FinalResponse
from app.orchestrator.services.student_orchestrator import StudentOrchestrator

logger = logging.getLogger(__name__)


class NexusChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    conversation_id: str | None = None
    student_id: str | int | None = None
    context: dict[str, Any] = Field(default_factory=dict)


class NexusWorkflowEvent(BaseModel):
    status: str
    detail: str | None = None


class NexusChatResponse(BaseModel):
    conversation_id: str
    response: str
    intent: str | None = None
    confidence: float | None = None
    activated_agents: list[str] = Field(default_factory=list)
    workflow: list[NexusWorkflowEvent] = Field(default_factory=list)
    activated_modules: list[str] = Field(default_factory=list)
    execution_time: float
    status: str
    warnings: list[str] = Field(default_factory=list)
    current_intent: str | None = None
    module_outputs: list[dict[str, Any]] = Field(default_factory=list)
    academic_plan: dict[str, Any] | None = None
    schedule_plan: dict[str, Any] | None = None
    comparison_plan: dict[str, Any] | None = None


class NexusService:
    """Application boundary for Nexus chat requests.

    This service intentionally delegates orchestration to StudentOrchestrator and
    only adapts request/response contracts for the Nexus API.
    """

    def __init__(self, db: AsyncSession | None = None) -> None:
        self.db = db

    async def send_message(self, request: NexusChatRequest) -> NexusChatResponse:
        conversation_id = request.conversation_id or str(uuid4())
        user_id = _coerce_user_id(request.student_id)
        raw_plan_id = request.context.get("plan_id")
        plan_id = _coerce_plan_id(raw_plan_id)
        started_at = perf_counter()

        logger.info(
            "nexus.chat_received conversation_id=%s user_id=%s has_plan_id=%s",
            conversation_id,
            user_id,
            bool(raw_plan_id),
        )
        try:
            orchestrator = StudentOrchestrator(db=self.db)
            final_response = await orchestrator.run(
                user_id=user_id,
                plan_id=plan_id,
                query=request.message,
            )
            execution_time = round(perf_counter() - started_at, 3)
            response = _to_nexus_response(
                conversation_id=conversation_id,
                final_response=final_response,
                execution_time=execution_time,
            )
            logger.info(
                "nexus.chat_returned conversation_id=%s status=%s intent=%s",
                conversation_id,
                response.status,
                response.intent,
            )
            return response
        except Exception as exc:
            logger.exception(
                "nexus.chat_failed conversation_id=%s user_id=%s",
                conversation_id,
                user_id,
            )
            execution_time = round(perf_counter() - started_at, 3)
            return _error_response(
                conversation_id=conversation_id,
                error=exc,
                execution_time=execution_time,
            )


def _coerce_user_id(value: str | int | None) -> int:
    if value is None or value == "":
        return 1
    try:
        user_id = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("student_id must be numeric when provided.") from exc
    if user_id <= 0:
        raise ValueError("student_id must be greater than zero.")
    return user_id


def _coerce_plan_id(value: Any) -> UUID:
    if value:
        try:
            return UUID(str(value))
        except ValueError as exc:
            raise ValueError("context.plan_id must be a valid UUID when provided.") from exc
    return uuid4()


def _to_nexus_response(
    *,
    conversation_id: str,
    final_response: FinalResponse,
    execution_time: float,
) -> NexusChatResponse:
    metadata = final_response.metadata or {}
    intent = metadata.get("intent") if isinstance(metadata.get("intent"), dict) else {}
    activated_modules = list(
        metadata.get("activated_modules")
        if isinstance(metadata.get("activated_modules"), list)
        else []
    )
    if not activated_modules:
        activated_modules = [
            response.module_name
            for response in final_response.module_responses
            if response.module_name
        ]
    if not activated_modules:
        activated_modules = list(intent.get("target_modules") or [])
    warnings = [
        str(item)
        for item in metadata.get("warnings", [])
        if item
    ] if isinstance(metadata.get("warnings"), list) else []
    status = str(metadata.get("status") or "success")
    module_outputs = [
        response.model_dump(mode="json") for response in final_response.module_responses
    ]
    academic_plan = _extract_academic_plan(module_outputs)
    schedule_plan = _extract_schedule_plan(module_outputs)
    comparison_plan = _extract_comparison_plan(module_outputs)
    warnings = _merge_warnings(warnings, module_outputs)

    workflow = _workflow_from_metadata(
        status=status,
        intent=intent,
        activated_modules=activated_modules,
        execution_plan=metadata.get("execution_plan")
        if isinstance(metadata.get("execution_plan"), list)
        else [],
        warnings=warnings,
    )

    confidence = intent.get("confidence")
    return NexusChatResponse(
        conversation_id=conversation_id,
        response=final_response.message,
        intent=intent.get("intent"),
        confidence=confidence if isinstance(confidence, int | float) else None,
        activated_agents=[_format_module_name(module) for module in activated_modules],
        workflow=workflow,
        activated_modules=activated_modules,
        execution_time=execution_time,
        status=status,
        warnings=warnings,
        current_intent=intent.get("intent"),
        module_outputs=module_outputs,
        academic_plan=academic_plan,
        schedule_plan=schedule_plan,
        comparison_plan=comparison_plan,
    )


def _workflow_from_metadata(
    *,
    status: str,
    intent: dict[str, Any],
    activated_modules: list[str],
    execution_plan: list[Any],
    warnings: list[str],
) -> list[NexusWorkflowEvent]:
    workflow = [
        NexusWorkflowEvent(
            status="Intent detected",
            detail=str(intent.get("intent")) if intent.get("intent") else None,
        ),
    ]
    workflow.append(
        NexusWorkflowEvent(
            status="Workflow planned" if activated_modules else "No specialist selected",
            detail=" -> ".join(_format_module_name(module) for module in activated_modules)
            if activated_modules
            else None,
        )
    )
    for step in execution_plan:
        if not isinstance(step, dict):
            continue
        agent = str(step.get("agent") or _format_module_name(str(step.get("module_name") or "")))
        step_status = str(step.get("status") or "planned")
        produced = step.get("produced_context_keys")
        detail_parts = []
        if isinstance(produced, list) and produced:
            detail_parts.append("produced " + ", ".join(str(item) for item in produced))
        if step.get("error"):
            detail_parts.append(str(step["error"]))
        workflow.append(
            NexusWorkflowEvent(
                status=f"{agent} {step_status}",
                detail="; ".join(detail_parts) if detail_parts else None,
            )
        )
    if warnings:
        workflow.append(
            NexusWorkflowEvent(
                status="Completed with warnings",
                detail="; ".join(warnings),
            )
        )
    else:
        workflow.append(NexusWorkflowEvent(status="Response composed"))
    workflow.append(NexusWorkflowEvent(status=_display_status(status)))
    return workflow


def _error_response(
    *,
    conversation_id: str,
    error: Exception,
    execution_time: float,
) -> NexusChatResponse:
    message = (
        "EdPlan Orchestrator could not complete the request. "
        "Please try again or provide more context."
    )
    warning = f"{type(error).__name__}: {error}"
    return NexusChatResponse(
        conversation_id=conversation_id,
        response=message,
        workflow=[
            NexusWorkflowEvent(status="Request received"),
            NexusWorkflowEvent(status="Error", detail=warning),
        ],
        activated_modules=[],
        activated_agents=[],
        execution_time=execution_time,
        status="failure",
        warnings=[warning],
        current_intent=None,
        intent=None,
        confidence=None,
        module_outputs=[],
        academic_plan=None,
        schedule_plan=None,
        comparison_plan=None,
    )


def _format_module_name(module_name: str) -> str:
    aliases = {
        "academic_planning": "PathCrafter",
        "scheduling": "SchedulePilot",
        "Career": "CareerNavigator",
        "Finance": "FinanceGuide",
        "College Comparison": "UniversityAdvisor",
        "college_comparison": "UniversityAdvisor",
        "Academic Success": "Academic Success",
    }
    return aliases.get(module_name, module_name)


def _display_status(status: str) -> str:
    labels = {
        "success": "Completed",
        "partial_success": "Partially completed",
        "failure": "Failed",
        "needs_context": "Needs context",
        "needs_routing": "Needs routing",
    }
    return labels.get(status, status)


def _extract_academic_plan(module_outputs: list[dict[str, Any]]) -> dict[str, Any] | None:
    for output in module_outputs:
        if output.get("module_name") != "academic_planning":
            continue
        data = output.get("data") if isinstance(output.get("data"), dict) else {}
        plan = data.get("academic_plan")
        if isinstance(plan, dict):
            return plan
    return None


def _extract_schedule_plan(module_outputs: list[dict[str, Any]]) -> dict[str, Any] | None:
    for output in module_outputs:
        if output.get("module_name") != "scheduling":
            continue
        data = output.get("data") if isinstance(output.get("data"), dict) else {}
        schedule = data.get("schedule_plan")
        if isinstance(schedule, dict):
            return schedule
    return None


def _extract_comparison_plan(module_outputs: list[dict[str, Any]]) -> dict[str, Any] | None:
    for output in module_outputs:
        if output.get("module_name") not in {"college_comparison", "College Comparison"}:
            continue
        data = output.get("data") if isinstance(output.get("data"), dict) else {}
        comparison = data.get("comparison_plan")
        if isinstance(comparison, dict):
            return comparison
    return None


def _merge_warnings(
    warnings: list[str],
    module_outputs: list[dict[str, Any]],
) -> list[str]:
    merged = list(warnings)
    for output in module_outputs:
        metadata = output.get("metadata") if isinstance(output.get("metadata"), dict) else {}
        for item in metadata.get("warnings", []) if isinstance(metadata.get("warnings"), list) else []:
            if item:
                merged.append(str(item))
        data = output.get("data") if isinstance(output.get("data"), dict) else {}
        plan = data.get("academic_plan") if isinstance(data.get("academic_plan"), dict) else {}
        validation = plan.get("validation") if isinstance(plan.get("validation"), dict) else {}
        for warning in validation.get("warnings", []) if isinstance(validation.get("warnings"), list) else []:
            message = warning.get("message") if isinstance(warning, dict) else warning
            if message:
                merged.append(str(message))
        schedule = data.get("schedule_plan") if isinstance(data.get("schedule_plan"), dict) else {}
        for warning in schedule.get("warnings", []) if isinstance(schedule.get("warnings"), list) else []:
            if warning:
                merged.append(str(warning))
        comparison = data.get("comparison_plan") if isinstance(data.get("comparison_plan"), dict) else {}
        for warning in comparison.get("warnings", []) if isinstance(comparison.get("warnings"), list) else []:
            if warning:
                merged.append(str(warning))
    return _unique(merged)


def _unique(values: list[str]) -> list[str]:
    unique_values = []
    for value in values:
        if value not in unique_values:
            unique_values.append(value)
    return unique_values
