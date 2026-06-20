from __future__ import annotations

from collections.abc import Awaitable, Callable
from uuid import UUID

from app.orchestrator.execution.module_executor import ModuleExecutionResult
from app.orchestrator.graph.student_graph import (
    CONTEXT_LOADER,
    INTENT_ROUTER,
    MODULE_SELECTOR,
    MODULE_EXECUTOR,
    RESPONSE_COMPOSER,
    StudentGraph,
    StudentGraphNode,
    build_context_loader_node,
    build_intent_router_node,
    build_module_executor_node,
    build_module_selector_node,
    build_response_composer_node,
    compose_response_node,
    execute_modules_node,
    load_context_node,
    route_intent_node,
    select_modules_node,
)
from app.orchestrator.schemas.intent_result import IntentResult
from app.orchestrator.schemas.module_response import FinalResponse
from app.orchestrator.schemas.student_context import StudentContext


ContextLoaderCallable = Callable[[int, UUID, str], Awaitable[StudentContext]]
IntentRouterCallable = Callable[[str, StudentContext | None], IntentResult]
ModuleSelectorCallable = Callable[[IntentResult], object]
ModuleExecutorCallable = Callable[
    [list[str], StudentContext, str], Awaitable[dict[str, ModuleExecutionResult]]
]
ResponseComposerCallable = Callable[
    [StudentContext | None, IntentResult | None, dict[str, ModuleExecutionResult]], FinalResponse
]


def build_student_graph(
    context_loader: ContextLoaderCallable | None = None,
    intent_router: IntentRouterCallable | None = None,
    module_selector: ModuleSelectorCallable | None = None,
    module_executor: ModuleExecutorCallable | None = None,
    response_composer: ResponseComposerCallable | None = None,
) -> StudentGraph:
    """Build the student orchestration graph."""
    context_handler = (
        build_context_loader_node(context_loader)
        if context_loader is not None
        else load_context_node
    )
    intent_handler = (
        build_intent_router_node(intent_router) if intent_router is not None else route_intent_node
    )
    selection_handler = (
        build_module_selector_node(module_selector)
        if module_selector is not None
        else select_modules_node
    )
    execution_handler = (
        build_module_executor_node(module_executor)
        if module_executor is not None
        else execute_modules_node
    )
    composition_handler = (
        build_response_composer_node(response_composer)
        if response_composer is not None
        else compose_response_node
    )
    return StudentGraph(
        nodes=[
            StudentGraphNode(name=CONTEXT_LOADER, handler=context_handler),
            StudentGraphNode(name=INTENT_ROUTER, handler=intent_handler),
            StudentGraphNode(name=MODULE_SELECTOR, handler=selection_handler),
            StudentGraphNode(name=MODULE_EXECUTOR, handler=execution_handler),
            StudentGraphNode(name=RESPONSE_COMPOSER, handler=composition_handler),
        ]
    )
