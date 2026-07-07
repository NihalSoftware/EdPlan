from __future__ import annotations

from typing import Any

from app.orchestrator.execution.module_executor import ModuleExecutionResult
from app.orchestrator.router.module_selector import ACADEMIC_PLANNING
from app.orchestrator.schemas.intent_result import IntentResult
from app.orchestrator.schemas.module_response import FinalResponse, ModuleResponse
from app.orchestrator.schemas.student_context import StudentContext


class ResponseComposer:
    """Composes module execution results into the orchestrator response contract."""

    def compose(
        self,
        context: StudentContext | None,
        intent_result: IntentResult | None,
        module_results: dict[str, ModuleExecutionResult],
    ) -> FinalResponse:
        """Return a structured final response preserving module output content."""
        results = list(module_results.values())
        successful_responses = [
            result.response for result in results if result.success and result.response is not None
        ]
        status = self._status(results)
        warnings = self._warnings(results)
        activated_modules = self._activated_modules(intent_result, successful_responses, results)
        clarification = (
            None
            if successful_responses
            else self._missing_context_clarification(context, intent_result)
        )
        message = clarification or self._compose_message(
            successful_responses=successful_responses,
            results=results,
            intent_result=intent_result,
        )
        if clarification is not None:
            status = "needs_context"

        return FinalResponse(
            message=message,
            module_responses=successful_responses,
            metadata={
                "status": status,
                "intent": intent_result.model_dump() if intent_result is not None else None,
                "activated_modules": activated_modules,
                "execution_plan": self._execution_plan(results),
                "shared_context": self._shared_context_summary(results),
                "warnings": warnings,
                "module_count": len(results),
                "successful_module_count": len(successful_responses),
                "failed_module_count": len([result for result in results if not result.success]),
                "results": [self._serialize_result(result) for result in results],
                "context_loaded": context is not None,
            },
        )

    @staticmethod
    def _status(results: list[ModuleExecutionResult]) -> str:
        if not results:
            return "needs_routing"
        if all(result.success for result in results):
            return "success"
        if any(result.success for result in results):
            return "partial_success"
        return "failure"

    @staticmethod
    def _activated_modules(
        intent_result: IntentResult | None,
        successful_responses: list[ModuleResponse],
        results: list[ModuleExecutionResult],
    ) -> list[str]:
        modules = [
            response.module_name
            for response in successful_responses
            if response.module_name
        ]
        if not modules:
            modules = [
                result.module_name
                for result in results
                if result.module_name
            ]
        if not modules and intent_result is not None:
            modules = list(intent_result.target_modules)
        return _unique(modules)

    @staticmethod
    def _compose_message(
        *,
        successful_responses: list[ModuleResponse],
        results: list[ModuleExecutionResult],
        intent_result: IntentResult | None,
    ) -> str:
        content_parts = [
            response.content.strip()
            for response in successful_responses
            if isinstance(response.content, str) and response.content.strip()
        ]
        if len(content_parts) == 1:
            return content_parts[0]
        if len(content_parts) > 1:
            return "Here is the coordinated EdPlan workflow result:\n\n" + "\n\n".join(
                f"{_display_module_name(response.module_name)}:\n{response.content.strip()}"
                for response in successful_responses
                if isinstance(response.content, str) and response.content.strip()
            )

        failed_results = [result for result in results if not result.success]
        if failed_results:
            unavailable = [
                result.module_name
                for result in failed_results
                if result.error == "Module not yet implemented"
            ]
            if unavailable:
                return (
                    "I understood your request, but the selected specialist is not available "
                    f"yet: {', '.join(unavailable)}."
                )
            return (
                "I could not complete the request because the selected specialist failed: "
                + "; ".join(
                    f"{result.module_name}: {result.error or 'Unknown error'}"
                    for result in failed_results
                )
            )

        if intent_result is None or not intent_result.target_modules:
            return (
                "I can help with academic planning, schedules, university comparison, "
                "financial guidance, career planning, or academic success. What would you "
                "like to work on?"
            )
        return "I understood your request, but no specialist produced a response."

    @staticmethod
    def _missing_context_clarification(
        context: StudentContext | None,
        intent_result: IntentResult | None,
    ) -> str | None:
        if intent_result is None or ACADEMIC_PLANNING not in intent_result.target_modules:
            return None
        if context is None:
            return (
                "I'll be happy to create your academic plan. First, which university "
                "and program are you pursuing?"
            )
        missing: list[str] = []
        if not context.university:
            missing.append("university")
        if not context.program:
            missing.append("program")
        if not context.plan:
            missing.append("academic plan")
        if not missing:
            return None
        if "university" in missing and "program" in missing:
            return (
                "I'll be happy to create your academic plan. First, which university "
                "and program are you pursuing?"
            )
        return (
            "I'll be happy to help with your academic plan. First, please provide your "
            f"{', '.join(missing)}."
        )

    @staticmethod
    def _warnings(results: list[ModuleExecutionResult]) -> list[str]:
        warnings: list[str] = []
        for result in results:
            if result.error:
                warnings.append(f"{result.module_name}: {result.error}")
            response = result.response
            if response is None:
                continue
            metadata_warnings = response.metadata.get("warnings")
            if isinstance(metadata_warnings, list):
                warnings.extend(str(item) for item in metadata_warnings if item)
            metadata_errors = response.metadata.get("errors")
            if isinstance(metadata_errors, list):
                warnings.extend(str(item) for item in metadata_errors if item)
        return _unique(warnings)

    @staticmethod
    def _execution_plan(results: list[ModuleExecutionResult]) -> list[dict[str, object]]:
        plan = []
        for index, result in enumerate(results, start=1):
            response = result.response
            metadata = response.metadata if response is not None else {}
            step = metadata.get("workflow_step") if isinstance(metadata, dict) else None
            if not isinstance(step, dict):
                step = {
                    "step": index,
                    "module_name": result.module_name,
                    "depends_on": [],
                    "consumes": [],
                    "provides": [],
                    "continue_on_failure": True,
                }
            plan.append(
                {
                    **step,
                    "module_name": result.module_name,
                    "agent": _display_module_name(result.module_name),
                    "status": "completed" if result.success else "failed",
                    "error": result.error,
                    "execution_time_ms": result.execution_time_ms,
                }
            )
        return plan

    @staticmethod
    def _shared_context_summary(results: list[ModuleExecutionResult]) -> dict[str, object]:
        produced: list[str] = []
        consumed: list[str] = []
        for result in results:
            response = result.response
            if response is None:
                continue
            step = response.metadata.get("workflow_step")
            if not isinstance(step, dict):
                continue
            produced.extend(
                str(item)
                for item in step.get("produced_context_keys", [])
                if item
            )
            consumed.extend(
                str(item)
                for item in step.get("consumed_context_keys", [])
                if item
            )
        return {
            "produced_keys": _unique(produced),
            "consumed_keys": _unique(consumed),
        }

    @staticmethod
    def _serialize_result(result: ModuleExecutionResult) -> dict[str, object]:
        payload = result.model_dump()
        response = result.response
        payload["response"] = (
            ResponseComposer._serialize_response(response) if response is not None else None
        )
        return payload

    @staticmethod
    def _serialize_response(response: ModuleResponse) -> dict[str, object]:
        return response.model_dump()


def _unique(values: list[Any]) -> list[Any]:
    unique_values = []
    for value in values:
        if value not in unique_values:
            unique_values.append(value)
    return unique_values


def _display_module_name(module_name: str) -> str:
    aliases = {
        "academic_planning": "PathCrafter",
        "scheduling": "SchedulePilot",
        "College Comparison": "UniversityAdvisor",
        "college_comparison": "UniversityAdvisor",
    }
    return aliases.get(module_name, module_name)
