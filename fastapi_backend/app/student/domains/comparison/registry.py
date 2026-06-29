from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.orchestrator.llm.base_provider import BaseLLMProvider
from app.orchestrator.modules.module_registry import ModuleRegistry
from app.orchestrator.router.module_selector import COLLEGE_COMPARISON
from app.student.domains.comparison.module import CollegeComparisonModule

MODULE_REGISTRY_NAME = COLLEGE_COMPARISON


def register_module(
    registry: ModuleRegistry,
    *,
    db: AsyncSession | None = None,
    llm_provider: BaseLLMProvider | None = None,
) -> CollegeComparisonModule:
    module = CollegeComparisonModule(db=db, llm_provider=llm_provider)
    if not registry.exists(MODULE_REGISTRY_NAME):
        registry.register(module, name=MODULE_REGISTRY_NAME)
    return module
