from __future__ import annotations

import logging
from time import perf_counter

from pydantic import BaseModel, Field

from app.orchestrator.modules.base_module import BaseModule
from app.orchestrator.modules.module_registry import ModuleRegistry
from app.orchestrator.schemas.module_response import ModuleResponse
from app.orchestrator.schemas.student_context import StudentContext

logger = logging.getLogger(__name__)


class ModuleExecutionResult(BaseModel):
    """Packaged result of a single orchestrator module execution."""

    module_name: str = Field(..., min_length=1)
    success: bool
    execution_time_ms: int = Field(..., ge=0)
    response: ModuleResponse | None = None
    error: str | None = None


class ModuleExecutor:
    """Executes modules and normalizes timing, success, and error metadata."""

    def __init__(self, registry: ModuleRegistry | None = None) -> None:
        self.registry = registry or ModuleRegistry()

    async def execute_selected(
        self,
        selected_modules: list[str],
        context: StudentContext,
        query: str,
    ) -> dict[str, ModuleExecutionResult]:
        """Execute selected modules by name and return results keyed by module name."""
        results: dict[str, ModuleExecutionResult] = {}
        for module_name in selected_modules:
            if module_name in results:
                continue
            results[module_name] = await self.execute_by_name(module_name, context, query)
        return results

    async def execute_by_name(
        self,
        module_name: str,
        context: StudentContext,
        query: str,
    ) -> ModuleExecutionResult:
        """Resolve and execute a module by name without leaking registry errors."""
        start_time = perf_counter()
        try:
            module = self.registry.get(module_name)
        except KeyError:
            return ModuleExecutionResult(
                module_name=module_name,
                success=False,
                execution_time_ms=self._elapsed_ms(start_time),
                response=None,
                error="Module not yet implemented",
            )
        return await self.execute(module, context, query)

    async def execute(
        self,
        module: BaseModule,
        context: StudentContext,
        query: str,
    ) -> ModuleExecutionResult:
        """Execute a module and return a structured execution result."""
        start_time = perf_counter()
        try:
            response = await module.execute(context=context, query=query)
            if not isinstance(response, ModuleResponse):
                raise TypeError("Module execute must return ModuleResponse.")
        except Exception as exc:
            execution_time_ms = self._elapsed_ms(start_time)
            logger.exception("Module execution failed module_name=%s", module.name)
            return ModuleExecutionResult(
                module_name=module.name,
                success=False,
                execution_time_ms=execution_time_ms,
                error=str(exc),
            )

        return ModuleExecutionResult(
            module_name=module.name,
            success=True,
            execution_time_ms=self._elapsed_ms(start_time),
            response=response,
        )

    @staticmethod
    def _elapsed_ms(start_time: float) -> int:
        return max(0, round((perf_counter() - start_time) * 1000))
