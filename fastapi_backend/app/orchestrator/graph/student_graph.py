from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from uuid import UUID

from app.orchestrator.execution.module_executor import ModuleExecutionResult
from app.orchestrator.schemas.intent_result import IntentResult
from app.orchestrator.schemas.module_response import FinalResponse
from app.orchestrator.schemas.student_context import StudentContext
from app.orchestrator.schemas.workflow_event import WorkflowEvent
from app.orchestrator.state.edplan_state import EdPlanState

START = "START"
CONTEXT_LOADER = "ContextLoader"
INTENT_ROUTER = "IntentRouter"
MODULE_SELECTOR = "ModuleSelector"
MODULE_EXECUTOR = "ModuleExecutor"
RESPONSE_COMPOSER = "ResponseComposer"
END = "END"

StudentGraphNodeHandler = Callable[[EdPlanState], Awaitable[EdPlanState]]


@dataclass(frozen=True)
class StudentGraphNode:
    """Named async node in the student orchestration graph."""

    name: str
    handler: StudentGraphNodeHandler


class StudentGraph:
    """Dependency-free graph foundation that can later be replaced by LangGraph."""

    def __init__(self, nodes: list[StudentGraphNode]) -> None:
        self.nodes = nodes

    async def execute(self, state: EdPlanState) -> EdPlanState:
        """Run graph nodes in sequence and return the resulting state."""
        self._record_event(state, START)
        for node in self.nodes:
            self._record_event(state, node.name)
            state = await node.handler(state)
        self._record_event(state, END)
        return state

    @staticmethod
    def _record_event(state: EdPlanState, event_type: str) -> None:
        state.workflow_events.append(WorkflowEvent(event_type=event_type))


async def load_context_node(state: EdPlanState) -> EdPlanState:
    """Placeholder context node with no database access."""
    if state.student_context is None:
        state.student_context = StudentContext()
    return state


def build_context_loader_node(
    loader: Callable[[int, UUID, str], Awaitable[StudentContext]],
) -> StudentGraphNodeHandler:
    """Build a ContextLoader graph node bound to a loader callable."""

    async def context_loader_node(state: EdPlanState) -> EdPlanState:
        state.student_context = await loader(state.user_id, state.plan_id, state.query)
        return state

    return context_loader_node


async def route_intent_node(state: EdPlanState) -> EdPlanState:
    """Placeholder intent node with no LLM or routing implementation."""
    if state.intent_result is None:
        state.intent_result = IntentResult(
            intent="unclassified",
            confidence=0.0,
            target_modules=[],
            reasoning="Placeholder intent result; routing is not implemented.",
        )
    state.selected_modules = list(state.intent_result.target_modules)
    return state


def build_intent_router_node(
    router: Callable[[str, StudentContext | None], IntentResult],
) -> StudentGraphNodeHandler:
    """Build an IntentRouter graph node bound to a router callable."""

    async def intent_router_node(state: EdPlanState) -> EdPlanState:
        state.intent_result = router(state.query, state.student_context)
        return state

    return intent_router_node


async def select_modules_node(state: EdPlanState) -> EdPlanState:
    """Placeholder module selector that mirrors routed target modules."""
    if state.intent_result is not None:
        state.selected_modules = list(state.intent_result.target_modules)
    return state


def build_module_selector_node(
    selector: Callable[[IntentResult], object],
) -> StudentGraphNodeHandler:
    """Build a ModuleSelector graph node bound to a selector callable."""

    async def module_selector_node(state: EdPlanState) -> EdPlanState:
        if state.intent_result is None:
            state.selected_modules = []
            return state
        selection = selector(state.intent_result)
        selected_modules = getattr(selection, "selected_modules", [])
        state.selected_modules = list(selected_modules)
        if hasattr(selection, "model_dump"):
            state.metadata["module_selection"] = selection.model_dump()
        return state

    return module_selector_node


def build_module_executor_node(
    executor: Callable[
        [list[str], StudentContext, str], Awaitable[dict[str, ModuleExecutionResult]]
    ],
) -> StudentGraphNodeHandler:
    """Build a ModuleExecutor graph node bound to an executor callable."""

    async def module_executor_node(state: EdPlanState) -> EdPlanState:
        context = state.student_context or StudentContext()
        state.module_results = await executor(state.selected_modules, context, state.query)
        return state

    return module_executor_node


async def execute_modules_node(state: EdPlanState) -> EdPlanState:
    """Placeholder module execution node; no modules are executed."""
    return state


def build_response_composer_node(
    composer: Callable[
        [StudentContext | None, IntentResult | None, dict[str, ModuleExecutionResult]],
        FinalResponse,
    ],
) -> StudentGraphNodeHandler:
    """Build a ResponseComposer graph node bound to a composer callable."""

    async def response_composer_node(state: EdPlanState) -> EdPlanState:
        state.final_response = composer(
            state.student_context,
            state.intent_result,
            state.module_results,
        )
        return state

    return response_composer_node


async def compose_response_node(state: EdPlanState) -> EdPlanState:
    """Placeholder response composer with no business-specific response logic."""
    if state.final_response is None:
        state.final_response = FinalResponse(
            message="Student orchestrator foundation executed successfully.",
            module_responses=[
                result.response
                for result in state.module_results.values()
                if result.success and result.response is not None
            ],
        )
    return state
