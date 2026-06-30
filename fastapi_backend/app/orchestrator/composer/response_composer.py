from __future__ import annotations

from app.orchestrator.execution.module_executor import ModuleExecutionResult
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
        """Return a structured final response without LLM or domain-specific logic."""
        results = list(module_results.values())
        successful_responses = [
            result.response for result in results if result.success and result.response is not None
        ]
        status = self._status(results)

        return FinalResponse(
            message=status,
            module_responses=successful_responses,
            metadata={
                "status": status,
                "intent": intent_result.model_dump() if intent_result is not None else None,
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
            return "no_modules_selected"
        if all(result.success for result in results):
            return "success"
        if any(result.success for result in results):
            return "partial_success"
        return "failure"

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
