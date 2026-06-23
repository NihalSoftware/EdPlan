from __future__ import annotations

from uuid import uuid4

import pytest

from app.orchestrator.execution.module_executor import ModuleExecutionResult
from app.orchestrator.graph.graph_builder import build_student_graph
from app.orchestrator.graph.student_graph import (
    CONTEXT_LOADER,
    END,
    INTENT_ROUTER,
    MEMORY_MANAGER,
    MODULE_EXECUTOR,
    MODULE_SELECTOR,
    RESPONSE_COMPOSER,
    START,
)
from app.orchestrator.router.module_selector import ACADEMIC_PLANNING
from app.orchestrator.schemas.intent_result import IntentResult
from app.orchestrator.schemas.module_response import FinalResponse, ModuleResponse
from app.orchestrator.schemas.student_context import StudentContext
from app.orchestrator.state.edplan_state import EdPlanState


@pytest.mark.asyncio
async def test_student_graph_executes_langgraph_workflow_in_order():
    async def load_context(user_id, plan_id, query):
        return StudentContext(user={"id": user_id}, plan={"plan_id": str(plan_id)})

    def route_intent(query, context):
        return IntentResult(
            intent="academic_planning",
            confidence=0.8,
            target_modules=[ACADEMIC_PLANNING],
        )

    def select_modules(intent_result):
        return type("Selection", (), {"selected_modules": list(intent_result.target_modules)})()

    async def execute_modules(selected_modules, context, query):
        return {
            ACADEMIC_PLANNING: ModuleExecutionResult(
                module_name=ACADEMIC_PLANNING,
                success=True,
                execution_time_ms=1,
                response=ModuleResponse(module_name=ACADEMIC_PLANNING, content="ok"),
            )
        }

    def compose_response(context, intent_result, module_results):
        return FinalResponse(message="success")

    async def update_memory(state):
        state.metadata["memory_updated"] = True

    graph = build_student_graph(
        context_loader=load_context,
        intent_router=route_intent,
        module_selector=select_modules,
        module_executor=execute_modules,
        response_composer=compose_response,
        memory_manager=update_memory,
    )

    completed_state = await graph.execute(
        EdPlanState(user_id=1, plan_id=uuid4(), query="What should I take?")
    )

    assert completed_state.student_context is not None
    assert completed_state.intent_result is not None
    assert completed_state.selected_modules == [ACADEMIC_PLANNING]
    assert completed_state.module_results[ACADEMIC_PLANNING].success is True
    assert completed_state.final_response is not None
    assert completed_state.metadata["memory_updated"] is True
    assert [event.event_type for event in completed_state.workflow_events] == [
        START,
        CONTEXT_LOADER,
        INTENT_ROUTER,
        MODULE_SELECTOR,
        MODULE_EXECUTOR,
        RESPONSE_COMPOSER,
        MEMORY_MANAGER,
        END,
    ]
