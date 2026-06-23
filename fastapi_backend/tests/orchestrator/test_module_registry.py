from __future__ import annotations

import pytest

from app.orchestrator.modules.base_module import BaseModule
from app.orchestrator.modules.example_module import EXAMPLE_MODULE, ExampleModule
from app.orchestrator.modules.module_registry import ModuleRegistry
from app.orchestrator.schemas.module_response import ModuleResponse
from app.orchestrator.schemas.student_context import StudentContext


class BlankNameModule(BaseModule):
    name = " "

    async def execute(self, context: StudentContext, query: str) -> ModuleResponse:
        return ModuleResponse(module_name="BlankNameModule")


class SyncExecuteModule(BaseModule):
    name = "SyncExecuteModule"

    def execute(self, context: StudentContext, query: str) -> ModuleResponse:
        return ModuleResponse(module_name=self.name)


def test_module_registry_registers_and_discovers_module():
    registry = ModuleRegistry()

    registry.register(ExampleModule())

    assert registry.exists(EXAMPLE_MODULE)
    assert registry.get(EXAMPLE_MODULE).name == EXAMPLE_MODULE
    assert registry.list_modules() == [EXAMPLE_MODULE]


def test_module_registry_rejects_duplicate_module_name():
    registry = ModuleRegistry()
    registry.register(ExampleModule())

    with pytest.raises(ValueError, match="already registered"):
        registry.register(ExampleModule())


def test_module_registry_rejects_non_base_module():
    registry = ModuleRegistry()

    with pytest.raises(TypeError, match="BaseModule"):
        registry.register(object())  # type: ignore[arg-type]


def test_module_registry_rejects_blank_module_name():
    registry = ModuleRegistry()

    with pytest.raises(ValueError, match="Module name is required"):
        registry.register(BlankNameModule())


def test_module_registry_rejects_sync_execute_method():
    registry = ModuleRegistry()

    with pytest.raises(TypeError, match="execute method must be async"):
        registry.register(SyncExecuteModule())
