from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.orchestrator.composer.response_composer import ResponseComposer
from app.orchestrator.context.context_loader import ContextLoader
from app.orchestrator.execution.module_executor import ModuleExecutor
from app.orchestrator.graph.graph_builder import build_student_graph
from app.orchestrator.graph.student_graph import StudentGraph
from app.orchestrator.modules.module_registry import ModuleRegistry
from app.orchestrator.router.intent_router import IntentRouter
from app.orchestrator.router.module_selector import ModuleSelector
from app.orchestrator.schemas.module_response import FinalResponse
from app.orchestrator.state.edplan_state import EdPlanState


class StudentOrchestrator:
    """Application service for running the student orchestration framework."""

    def __init__(
        self,
        db: AsyncSession | None = None,
        context_loader: ContextLoader | None = None,
        intent_router: IntentRouter | None = None,
        module_selector: ModuleSelector | None = None,
        module_registry: ModuleRegistry | None = None,
        module_executor: ModuleExecutor | None = None,
        response_composer: ResponseComposer | None = None,
        graph: StudentGraph | None = None,
    ) -> None:
        self.module_registry = module_registry or ModuleRegistry()
        self.context_loader = context_loader or (ContextLoader(db) if db is not None else None)
        self.intent_router = intent_router or IntentRouter()
        self.module_selector = module_selector or ModuleSelector(registry=self.module_registry)
        self.module_executor = module_executor or ModuleExecutor(registry=self.module_registry)
        self.response_composer = response_composer or ResponseComposer()
        self.graph = graph or build_student_graph(
            context_loader=self.context_loader.load if self.context_loader is not None else None,
            intent_router=self.intent_router.route,
            module_selector=self.module_selector.select,
            module_executor=self.module_executor.execute_selected,
            response_composer=self.response_composer.compose,
        )

    async def run(self, user_id: int, plan_id: UUID, query: str) -> FinalResponse:
        """Initialize orchestration state, execute the graph, and return a response."""
        state = EdPlanState(user_id=user_id, plan_id=plan_id, query=query)
        completed_state = await self.graph.execute(state)
        if completed_state.final_response is None:
            raise RuntimeError("Student orchestration completed without a final response.")
        return completed_state.final_response
