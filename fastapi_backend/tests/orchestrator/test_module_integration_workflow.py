from __future__ import annotations

from uuid import uuid4

import pytest

from app.orchestrator.modules.example_module import EXAMPLE_MODULE, ExampleModule
from app.orchestrator.modules.base_module import BaseModule
from app.orchestrator.modules.module_registry import ModuleRegistry
from app.orchestrator.router.module_selector import (
    ACADEMIC_PLANNING,
    COLLEGE_COMPARISON,
    SCHEDULING,
)
from app.orchestrator.schemas.intent_result import IntentResult
from app.orchestrator.schemas.module_response import ModuleResponse
from app.orchestrator.schemas.student_context import StudentContext
from app.orchestrator.services.student_orchestrator import StudentOrchestrator


class ExampleIntentRouter:
    def route(self, query: str, context: StudentContext | None = None) -> IntentResult:
        return IntentResult(
            intent="example_module_integration",
            confidence=1.0,
            target_modules=[EXAMPLE_MODULE],
            reasoning="Test-only router for module integration readiness.",
        )


class MultiAgentIntentRouter:
    def route(self, query: str, context: StudentContext | None = None) -> IntentResult:
        return IntentResult(
            intent="multi_module",
            confidence=0.95,
            target_modules=[SCHEDULING, COLLEGE_COMPARISON, ACADEMIC_PLANNING],
            reasoning="Test-only mixed academic planning workflow.",
        )


class FakeContextLoader:
    async def load(self, user_id, plan_id, query):
        return StudentContext(
            user={"id": user_id},
            plan={"plan_id": str(plan_id)},
            program={"name": "Reference Program"},
            university={"name": "Reference University"},
        )


class RecordingModule(BaseModule):
    def __init__(
        self,
        name: str,
        content: str,
        output_key: str,
        output: dict,
        seen: list[tuple[str, list[str]]],
    ) -> None:
        self.name = name
        self.description = name
        self.content = content
        self.output_key = output_key
        self.output = output
        self.seen = seen

    async def execute(self, context: StudentContext, query: str) -> ModuleResponse:
        self.seen.append((self.name, sorted(context.orchestrator_outputs.keys())))
        return ModuleResponse(
            module_name=self.name,
            content=self.content,
            data={self.output_key: self.output},
            metadata={"warnings": []},
        )


@pytest.mark.asyncio
async def test_end_to_end_langgraph_execution_with_example_module():
    registry = ModuleRegistry()
    registry.register(ExampleModule())
    orchestrator = StudentOrchestrator(
        context_loader=FakeContextLoader(),
        intent_router=ExampleIntentRouter(),
        module_registry=registry,
    )

    response = await orchestrator.run(
        user_id=1,
        plan_id=uuid4(),
        query="Run the example module.",
    )

    assert response.message == "ExampleModule executed through the orchestrator."
    assert response.module_responses[0].module_name == EXAMPLE_MODULE
    assert response.module_responses[0].metadata["reference_module"] is True
    assert response.metadata["intent"]["intent"] == "example_module_integration"


@pytest.mark.asyncio
async def test_orchestrator_executes_multi_agent_plan_with_structured_handoffs():
    seen: list[tuple[str, list[str]]] = []
    registry = ModuleRegistry()
    registry.register(
        RecordingModule(
            ACADEMIC_PLANNING,
            "Academic plan ready.",
            "academic_plan",
            {"remaining_credits": 60, "graduation_estimate": "4 semesters"},
            seen,
        )
    )
    registry.register(
        RecordingModule(
            SCHEDULING,
            "Schedule ready.",
            "schedule_plan",
            {"summary": {"recommended_credits": 15}},
            seen,
        )
    )
    registry.register(
        RecordingModule(
            COLLEGE_COMPARISON,
            "University comparison ready.",
            "comparison_plan",
            {"recommended_university": {"university_name": "NNMC"}},
            seen,
        )
    )
    orchestrator = StudentOrchestrator(
        context_loader=FakeContextLoader(),
        intent_router=MultiAgentIntentRouter(),
        module_registry=registry,
    )

    response = await orchestrator.run(
        user_id=1,
        plan_id=uuid4(),
        query="Create my academic plan, build my schedule, and compare transfer options.",
    )

    assert [name for name, _ in seen] == [
        ACADEMIC_PLANNING,
        SCHEDULING,
        COLLEGE_COMPARISON,
    ]
    assert seen[1][1] == ["academic_plan", ACADEMIC_PLANNING]
    assert "schedule_plan" in seen[2][1]
    assert [item["module_name"] for item in response.metadata["execution_plan"]] == [
        ACADEMIC_PLANNING,
        SCHEDULING,
        COLLEGE_COMPARISON,
    ]
    assert response.metadata["shared_context"]["produced_keys"] == [
        "academic_plan",
        "schedule_plan",
        "comparison_plan",
        "recommended_university",
    ]
    assert response.message.startswith("Here is the coordinated EdPlan workflow result:")
