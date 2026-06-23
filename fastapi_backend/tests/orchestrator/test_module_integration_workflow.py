from __future__ import annotations

from uuid import uuid4

import pytest

from app.orchestrator.modules.example_module import EXAMPLE_MODULE, ExampleModule
from app.orchestrator.modules.module_registry import ModuleRegistry
from app.orchestrator.schemas.intent_result import IntentResult
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


class FakeContextLoader:
    async def load(self, user_id, plan_id, query):
        return StudentContext(
            user={"id": user_id},
            plan={"plan_id": str(plan_id)},
            program={"name": "Reference Program"},
            university={"name": "Reference University"},
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

    assert response.message == "success"
    assert response.module_responses[0].module_name == EXAMPLE_MODULE
    assert response.module_responses[0].metadata["reference_module"] is True
    assert response.metadata["intent"]["intent"] == "example_module_integration"
