from __future__ import annotations

from time import perf_counter
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.orchestrator.schemas.module_response import FinalResponse
from app.orchestrator.services.student_orchestrator import StudentOrchestrator


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
    workflow: list[NexusWorkflowEvent] = Field(default_factory=list)
    activated_modules: list[str] = Field(default_factory=list)
    execution_time: float
    current_intent: str | None = None
    confidence: float | None = None


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

        orchestrator = StudentOrchestrator(db=self.db if raw_plan_id else None)
        final_response = await orchestrator.run(
            user_id=user_id,
            plan_id=plan_id,
            query=request.message,
        )

        execution_time = round(perf_counter() - started_at, 3)
        return _to_nexus_response(
            conversation_id=conversation_id,
            final_response=final_response,
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
    activated_modules = [
        response.module_name
        for response in final_response.module_responses
        if response.module_name
    ]
    if not activated_modules:
        activated_modules = list(intent.get("target_modules") or [])

    workflow = [
        NexusWorkflowEvent(status="Understanding Goal..."),
        NexusWorkflowEvent(
            status=_routing_status(activated_modules),
            detail=", ".join(activated_modules) if activated_modules else None,
        ),
        NexusWorkflowEvent(status="Generating Response..."),
        NexusWorkflowEvent(status="Completed"),
    ]

    confidence = intent.get("confidence")
    return NexusChatResponse(
        conversation_id=conversation_id,
        response=final_response.message,
        workflow=workflow,
        activated_modules=activated_modules,
        execution_time=execution_time,
        current_intent=intent.get("intent"),
        confidence=confidence if isinstance(confidence, int | float) else None,
    )


def _routing_status(activated_modules: list[str]) -> str:
    if not activated_modules:
        return "Routing to Orchestrator..."
    if len(activated_modules) == 1:
        return f"Routing to {_format_module_name(activated_modules[0])}..."
    return "Routing to Specialized Agents..."


def _format_module_name(module_name: str) -> str:
    aliases = {
        "academic_planning": "PathCrafter",
        "scheduling": "SchedulePilot",
        "Career": "CareerNavigator",
        "Finance": "FinanceGuide",
        "College Comparison": "UniversityAdvisor",
        "Academic Success": "Academic Success",
    }
    return aliases.get(module_name, module_name)
