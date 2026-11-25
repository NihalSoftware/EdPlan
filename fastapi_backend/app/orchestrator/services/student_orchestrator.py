from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.orchestrator.composer.response_composer import ResponseComposer
from app.orchestrator.context.context_loader import ContextLoader
from app.orchestrator.execution.module_executor import ModuleExecutionResult, ModuleExecutor
from app.orchestrator.graph.graph_builder import build_student_graph
from app.orchestrator.graph.student_graph import StudentGraph
from app.orchestrator.llm.base_provider import BaseLLMProvider
from app.orchestrator.memory.memory_manager import MemoryManager
from app.orchestrator.modules.module_registry import ModuleRegistry
from app.orchestrator.observability.run_tracker import RunTracker
from app.orchestrator.observability.workflow_tracker import (
    CONTEXT_LOADED,
    FAILURE,
    INTENT_IDENTIFIED,
    MEMORY_UPDATE_COMPLETED,
    MEMORY_UPDATE_FAILED,
    MEMORY_UPDATE_STARTED,
    MODULES_SELECTED,
    MODULE_EXECUTION_COMPLETED,
    MODULE_EXECUTION_STARTED,
    RESPONSE_COMPOSED,
    WorkflowTracker,
)
from app.orchestrator.router.intent_router import IntentRouter
from app.orchestrator.router.module_selector import (
    ACADEMIC_PLANNING,
    COLLEGE_COMPARISON,
    SCHEDULING,
    ModuleSelector,
)
from app.orchestrator.schemas.module_response import FinalResponse
from app.orchestrator.schemas.student_context import StudentContext
from app.orchestrator.state.edplan_state import EdPlanState
from app.student.domains.planning.module import (
    AcademicPlanningModule,
    MODULE_NAME as ACADEMIC_PLANNING_MODULE_NAME,
)
from app.student.domains.comparison.registry import register_module as register_comparison_module
from app.student.domains.scheduling.module import (
    MODULE_NAME as SCHEDULEPILOT_MODULE_NAME,
    SchedulePilotModule,
)

logger = logging.getLogger(__name__)


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
        llm_provider: BaseLLMProvider | None = None,
        memory_manager: MemoryManager | None = None,
        run_tracker: RunTracker | None = None,
        workflow_tracker: WorkflowTracker | None = None,
    ) -> None:
        self.module_registry = module_registry or ModuleRegistry()
        if db is not None and not self.module_registry.exists(ACADEMIC_PLANNING_MODULE_NAME):
            self.module_registry.register(
                AcademicPlanningModule(db=db, llm_provider=llm_provider)
            )
        if db is not None and not self.module_registry.exists(SCHEDULEPILOT_MODULE_NAME):
            self.module_registry.register(SchedulePilotModule(db=db))
        if db is not None:
            register_comparison_module(
                self.module_registry,
                db=db,
                llm_provider=llm_provider,
            )
        self.context_loader = context_loader or (ContextLoader(db) if db is not None else None)
        self.intent_router = intent_router or IntentRouter()
        self.module_selector = module_selector or ModuleSelector(registry=self.module_registry)
        self.module_executor = module_executor or ModuleExecutor(registry=self.module_registry)
        self.response_composer = response_composer or ResponseComposer()
        self.llm_provider = llm_provider
        self.memory_manager = memory_manager or MemoryManager(db)
        self.run_tracker = run_tracker or RunTracker(db)
        self.workflow_tracker = workflow_tracker or WorkflowTracker(db)
        self._graph_override = graph is not None
        self.graph = graph or build_student_graph(
            context_loader=self.context_loader.load if self.context_loader is not None else None,
            intent_router=self.intent_router.route,
            module_selector=self.module_selector.select,
            module_executor=self.module_executor.execute_selected,
            response_composer=self.response_composer.compose,
        )

    async def run(self, user_id: int, plan_id: UUID, query: str) -> FinalResponse:
        """Run the orchestration stages and persist durable execution trace data."""
        logger.info(
            "orchestrator.request_received user_id=%s plan_id=%s query_length=%s",
            user_id,
            plan_id,
            len(query),
        )
        state = EdPlanState(user_id=user_id, plan_id=plan_id, query=query)
        run = await self.run_tracker.create_run(user_id=user_id, plan_id=plan_id, query=query)
        await self.run_tracker.mark_running(run)
        stage_tracker = {"stage": "run_started"}

        try:
            execution_graph = (
                self.graph
                if self._graph_override
                else self._build_observable_graph(run, stage_tracker)
            )
            completed_state = await execution_graph.execute(state)
            if completed_state.final_response is None:
                raise RuntimeError("Student orchestration completed without a final response.")
            await self.run_tracker.complete_run(
                run,
                metadata={
                    "final_response": completed_state.final_response.model_dump(mode="json"),
                    "workflow_event_count": len(completed_state.workflow_events),
                },
            )

            logger.info(
                "orchestrator.response_returned user_id=%s plan_id=%s status=%s",
                user_id,
                plan_id,
                completed_state.final_response.metadata.get("status"),
            )
            return completed_state.final_response
        except Exception as exc:
            logger.exception(
                "orchestrator.request_failed user_id=%s plan_id=%s stage=%s",
                user_id,
                plan_id,
                stage_tracker["stage"],
            )
            await self.workflow_tracker.record_event(
                getattr(run, "run_id", None),
                FAILURE,
                {
                    "stage": stage_tracker["stage"],
                    "error": str(exc),
                    "exception_type": type(exc).__name__,
                },
            )
            await self.run_tracker.fail_run(run, exc)
            raise

    def _build_observable_graph(
        self,
        run: object,
        stage_tracker: dict[str, str],
    ) -> StudentGraph:
        run_id = getattr(run, "run_id", None)
        planned_workflow: list[dict[str, object]] = []

        async def load_context(user_id: int, plan_id: UUID, query: str) -> StudentContext:
            stage_tracker["stage"] = "context_loading"
            context = (
                await self.context_loader.load(user_id, plan_id, query)
                if self.context_loader is not None
                else StudentContext()
            )
            await self.workflow_tracker.record_event(
                run_id,
                CONTEXT_LOADED,
                _context_metadata_from_context(context),
            )
            return context

        def route_intent(query: str, context: StudentContext | None):
            stage_tracker["stage"] = "intent_routing"
            intent_result = self.intent_router.route(query, context)
            logger.info(
                "orchestrator.intent_detected intent=%s confidence=%s modules=%s",
                intent_result.intent,
                intent_result.confidence,
                intent_result.target_modules,
            )
            return intent_result

        async def record_intent(query: str, context: StudentContext | None):
            intent_result = route_intent(query, context)
            await self.run_tracker.update_intent(run, intent_result.intent)
            await self.workflow_tracker.record_event(
                run_id,
                INTENT_IDENTIFIED,
                intent_result.model_dump(mode="json"),
            )
            return intent_result

        def select_modules(intent_result):
            stage_tracker["stage"] = "module_selection"
            selection = self.module_selector.select(intent_result)
            logger.info(
                "orchestrator.modules_selected selected=%s unavailable=%s invalid=%s",
                selection.selected_modules,
                selection.unavailable_modules,
                selection.invalid_modules,
            )
            return selection

        async def record_module_selection(intent_result):
            nonlocal planned_workflow
            selection = select_modules(intent_result)
            planned_workflow = list(selection.execution_plan)
            await self.run_tracker.update_selected_modules(
                run,
                list(selection.selected_modules),
            )
            await self.workflow_tracker.record_event(
                run_id,
                MODULES_SELECTED,
                selection.model_dump(mode="json"),
            )
            return selection

        async def execute_modules(
            selected_modules: list[str],
            context: StudentContext,
            query: str,
        ):
            stage_tracker["stage"] = "module_execution"
            results = {}
            seen_modules: set[str] = set()
            shared_context = context.model_copy(deep=True)
            for step_index, module_name in enumerate(selected_modules, start=1):
                if module_name in seen_modules:
                    continue
                seen_modules.add(module_name)
                step = _workflow_step(planned_workflow, module_name, step_index)
                consumed_keys = _available_shared_output_keys(shared_context)
                logger.info("orchestrator.module_execution_started module=%s", module_name)
                await self.workflow_tracker.record_event(
                    run_id,
                    MODULE_EXECUTION_STARTED,
                    {
                        "module_name": module_name,
                        "step": step,
                        "consumed_context_keys": consumed_keys,
                    },
                )
                module_execution = await self.run_tracker.record_module_started(run, module_name)
                try:
                    result = await self.module_executor.execute_by_name(
                        module_name,
                        shared_context,
                        query,
                    )
                except Exception as exc:
                    logger.exception(
                        "orchestrator.module_execution_failed module=%s",
                        module_name,
                    )
                    result = ModuleExecutionResult(
                        module_name=module_name,
                        success=False,
                        execution_time_ms=0,
                        response=None,
                        error=str(exc),
                    )
                results[module_name] = result
                produced_keys = []
                if result.success and result.response is not None:
                    produced_keys = _apply_structured_handoff(
                        shared_context,
                        module_name,
                        result.response.data,
                    )
                    result.response.metadata["workflow_step"] = {
                        **step,
                        "status": "completed",
                        "consumed_context_keys": consumed_keys,
                        "produced_context_keys": produced_keys,
                    }
                elif result.response is not None:
                    result.response.metadata["workflow_step"] = {
                        **step,
                        "status": "failed",
                        "consumed_context_keys": consumed_keys,
                        "produced_context_keys": [],
                    }
                await self.run_tracker.record_module_completed(module_execution, result)
                logger.info(
                    "orchestrator.module_execution_completed module=%s success=%s duration_ms=%s",
                    module_name,
                    result.success,
                    result.execution_time_ms,
                )
                await self.workflow_tracker.record_event(
                    run_id,
                    MODULE_EXECUTION_COMPLETED,
                    {
                        **result.model_dump(mode="json"),
                        "step": step,
                        "consumed_context_keys": consumed_keys,
                        "produced_context_keys": produced_keys,
                    },
                )
            context.orchestrator_outputs = dict(shared_context.orchestrator_outputs)
            return results

        def compose_response(context, intent_result, module_results):
            stage_tracker["stage"] = "response_composition"
            response = self.response_composer.compose(context, intent_result, module_results)
            logger.info(
                "orchestrator.response_composed status=%s module_count=%s",
                response.metadata.get("status"),
                response.metadata.get("module_count"),
            )
            return response

        async def record_response(context, intent_result, module_results):
            response = compose_response(context, intent_result, module_results)
            await self.workflow_tracker.record_event(
                run_id,
                RESPONSE_COMPOSED,
                response.model_dump(mode="json"),
            )
            return response

        async def update_memory(state: EdPlanState) -> None:
            stage_tracker["stage"] = "memory_update"
            await self.workflow_tracker.record_event(
                run_id,
                MEMORY_UPDATE_STARTED,
                {"has_final_response": state.final_response is not None},
            )
            try:
                if run_id is None:
                    metadata: dict[str, object] = {
                        "memory_saved": False,
                        "reason": "run_id unavailable",
                    }
                else:
                    metadata = await self.memory_manager.update_memory(
                        user_id=state.user_id,
                        plan_id=state.plan_id,
                        run_id=run_id,
                        query=state.query,
                        response=state.final_response,
                    )
                await self.workflow_tracker.record_event(
                    run_id,
                    MEMORY_UPDATE_COMPLETED,
                    metadata,
                )
            except Exception as exc:
                await self.workflow_tracker.record_event(
                    run_id,
                    MEMORY_UPDATE_FAILED,
                    {"error": str(exc), "exception_type": type(exc).__name__},
                )

        return build_student_graph(
            context_loader=load_context,
            intent_router=record_intent,
            module_selector=record_module_selection,
            module_executor=execute_modules,
            response_composer=record_response,
            memory_manager=update_memory,
        )


def _context_metadata_from_context(context: StudentContext) -> dict[str, Any]:
    return {
        "context_loaded": True,
        "has_user": context.user is not None,
        "has_plan": context.plan is not None,
        "has_program": context.program is not None,
        "has_university": context.university is not None,
        "completed_course_count": len(context.completed_courses),
        "preference_count": len(context.preferences),
        "memory_count": len(context.memory),
        "shared_output_count": len(context.orchestrator_outputs),
    }


def _workflow_step(
    planned_workflow: list[dict[str, object]],
    module_name: str,
    fallback_index: int,
) -> dict[str, object]:
    for step in planned_workflow:
        if step.get("module_name") == module_name:
            return dict(step)
    return {
        "step": fallback_index,
        "module_name": module_name,
        "depends_on": [],
        "consumes": [],
        "provides": _provides_for_module(module_name),
        "continue_on_failure": True,
    }


def _available_shared_output_keys(context: StudentContext) -> list[str]:
    return sorted(key for key, value in context.orchestrator_outputs.items() if value is not None)


def _apply_structured_handoff(
    context: StudentContext,
    module_name: str,
    data: dict[str, Any],
) -> list[str]:
    produced: list[str] = []
    for key in ("academic_plan", "schedule_plan", "comparison_plan"):
        value = data.get(key)
        if isinstance(value, dict):
            context.orchestrator_outputs[key] = value
            context.orchestrator_outputs.setdefault(module_name, {})[key] = value
            produced.append(key)
    comparison = data.get("comparison_plan")
    if isinstance(comparison, dict):
        recommended = comparison.get("recommended_university")
        if isinstance(recommended, dict):
            context.orchestrator_outputs["recommended_university"] = recommended
            produced.append("recommended_university")
    academic_plan = data.get("academic_plan")
    if isinstance(academic_plan, dict):
        _merge_plan_hints(context, academic_plan)
    schedule_plan = data.get("schedule_plan")
    if isinstance(schedule_plan, dict):
        _merge_schedule_hints(context, schedule_plan)
    return _unique_strings(produced)


def _merge_plan_hints(context: StudentContext, academic_plan: dict[str, Any]) -> None:
    plan = dict(context.plan or {})
    for key in (
        "remaining_credits",
        "graduation_estimate",
        "completed_credits",
        "total_credits",
    ):
        if academic_plan.get(key) is not None:
            plan[key] = academic_plan[key]
    plan["latest_academic_plan"] = academic_plan
    context.plan = plan


def _merge_schedule_hints(context: StudentContext, schedule_plan: dict[str, Any]) -> None:
    plan = dict(context.plan or {})
    plan["latest_schedule_plan"] = schedule_plan
    summary = schedule_plan.get("summary")
    if isinstance(summary, dict):
        for source_key, target_key in (
            ("term_id", "selected_term_id"),
            ("term_name", "selected_term_name"),
            ("recommended_credits", "scheduled_credits"),
        ):
            if summary.get(source_key) is not None:
                plan[target_key] = summary[source_key]
    context.plan = plan


def _provides_for_module(module_name: str) -> list[str]:
    if module_name == ACADEMIC_PLANNING:
        return ["academic_plan"]
    if module_name == SCHEDULING:
        return ["schedule_plan"]
    if module_name == COLLEGE_COMPARISON:
        return ["comparison_plan", "recommended_university"]
    return []


def _unique_strings(values: list[str]) -> list[str]:
    unique: list[str] = []
    for value in values:
        if value not in unique:
            unique.append(value)
    return unique
