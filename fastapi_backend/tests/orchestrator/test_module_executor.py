from __future__ import annotations

import pytest

from app.orchestrator.execution.module_executor import ModuleExecutor
from app.orchestrator.modules.base_module import BaseModule
from app.orchestrator.modules.module_registry import ModuleRegistry
from app.orchestrator.router.module_selector import ACADEMIC_PLANNING, CAREER, FINANCE
from app.orchestrator.schemas.module_response import ModuleResponse
from app.orchestrator.schemas.student_context import StudentContext


class FakeModule(BaseModule):
    def __init__(self, name: str, should_fail: bool = False) -> None:
        self.name = name
        self.should_fail = should_fail

    async def execute(self, context: StudentContext, query: str) -> ModuleResponse:
        if self.should_fail:
            raise RuntimeError("planned failure")
        return ModuleResponse(module_name=self.name, content=f"{self.name} completed")


class InvalidResponseModule(BaseModule):
    name = "InvalidResponseModule"

    async def execute(self, context: StudentContext, query: str):
        return {"module_name": self.name}


def build_executor(*modules: FakeModule) -> ModuleExecutor:
    registry = ModuleRegistry()
    for module in modules:
        registry.register(module)
    return ModuleExecutor(registry=registry)


@pytest.mark.asyncio
async def test_module_executor_executes_single_module():
    result = await build_executor(FakeModule(ACADEMIC_PLANNING)).execute_selected(
        [ACADEMIC_PLANNING],
        StudentContext(),
        "Plan my courses",
    )

    assert list(result) == [ACADEMIC_PLANNING]
    assert result[ACADEMIC_PLANNING].success is True
    assert result[ACADEMIC_PLANNING].response is not None
    assert result[ACADEMIC_PLANNING].response.module_name == ACADEMIC_PLANNING


@pytest.mark.asyncio
async def test_module_executor_executes_multiple_modules():
    result = await build_executor(FakeModule(CAREER), FakeModule(FINANCE)).execute_selected(
        [CAREER, FINANCE],
        StudentContext(),
        "Compare career paths and financial aid",
    )

    assert list(result) == [CAREER, FINANCE]
    assert all(item.success for item in result.values())


@pytest.mark.asyncio
async def test_module_executor_returns_placeholder_for_missing_module():
    result = await ModuleExecutor().execute_selected(
        [CAREER],
        StudentContext(),
        "What career fits me?",
    )

    assert result[CAREER].success is False
    assert result[CAREER].response is None
    assert result[CAREER].error == "Module not yet implemented"


@pytest.mark.asyncio
async def test_module_executor_captures_module_failure():
    result = await build_executor(FakeModule(CAREER, should_fail=True)).execute_selected(
        [CAREER],
        StudentContext(),
        "What career fits me?",
    )

    assert result[CAREER].success is False
    assert result[CAREER].response is None
    assert result[CAREER].error == "planned failure"


@pytest.mark.asyncio
async def test_module_executor_handles_empty_module_list():
    result = await ModuleExecutor().execute_selected([], StudentContext(), "Explain EdPlan")

    assert result == {}


@pytest.mark.asyncio
async def test_module_executor_rejects_invalid_module_response():
    result = await build_executor(InvalidResponseModule()).execute_selected(
        ["InvalidResponseModule"],
        StudentContext(),
        "Run invalid module",
    )

    assert result["InvalidResponseModule"].success is False
    assert result["InvalidResponseModule"].response is None
    assert result["InvalidResponseModule"].error == "Module execute must return ModuleResponse."
