from __future__ import annotations

from app.orchestrator.composer.response_composer import ResponseComposer
from app.orchestrator.execution.module_executor import ModuleExecutionResult
from app.orchestrator.router.module_selector import ACADEMIC_PLANNING, CAREER, FINANCE
from app.orchestrator.schemas.intent_result import IntentResult
from app.orchestrator.schemas.module_response import ModuleResponse
from app.orchestrator.schemas.student_context import StudentContext


def success_result(module_name: str) -> ModuleExecutionResult:
    return ModuleExecutionResult(
        module_name=module_name,
        success=True,
        execution_time_ms=1,
        response=ModuleResponse(module_name=module_name, content="ok"),
    )


def failure_result(module_name: str, error: str = "Module not yet implemented"):
    return ModuleExecutionResult(
        module_name=module_name,
        success=False,
        execution_time_ms=1,
        error=error,
    )


def test_response_composer_composes_successful_response():
    final_response = ResponseComposer().compose(
        StudentContext(),
        IntentResult(
            intent="academic_planning",
            confidence=0.8,
            target_modules=[ACADEMIC_PLANNING],
        ),
        {ACADEMIC_PLANNING: success_result(ACADEMIC_PLANNING)},
    )

    assert final_response.message == "success"
    assert final_response.module_responses[0].module_name == ACADEMIC_PLANNING
    assert final_response.metadata["status"] == "success"
    assert final_response.metadata["successful_module_count"] == 1


def test_response_composer_composes_partial_success():
    final_response = ResponseComposer().compose(
        StudentContext(),
        IntentResult(intent="multi_module", confidence=0.9, target_modules=[CAREER, FINANCE]),
        {
            CAREER: success_result(CAREER),
            FINANCE: failure_result(FINANCE),
        },
    )

    assert final_response.message == "partial_success"
    assert [response.module_name for response in final_response.module_responses] == [CAREER]
    assert final_response.metadata["failed_module_count"] == 1


def test_response_composer_composes_full_failure():
    final_response = ResponseComposer().compose(
        StudentContext(),
        IntentResult(intent="multi_module", confidence=0.9, target_modules=[CAREER, FINANCE]),
        {
            CAREER: failure_result(CAREER),
            FINANCE: failure_result(FINANCE, "planned failure"),
        },
    )

    assert final_response.message == "failure"
    assert final_response.module_responses == []
    assert final_response.metadata["failed_module_count"] == 2
