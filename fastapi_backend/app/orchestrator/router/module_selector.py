from __future__ import annotations

from pydantic import BaseModel, Field

from app.orchestrator.modules.module_registry import ModuleRegistry
from app.orchestrator.schemas.intent_result import IntentResult

ACADEMIC_PLANNING = "academic_planning"
SCHEDULING = "Scheduling"
CAREER = "Career"
FINANCE = "Finance"
ACADEMIC_SUCCESS = "Academic Success"
COLLEGE_COMPARISON = "College Comparison"
EXAMPLE_MODULE = "ExampleModule"

OFFICIAL_MODULES: tuple[str, ...] = (
    ACADEMIC_PLANNING,
    SCHEDULING,
    CAREER,
    FINANCE,
    ACADEMIC_SUCCESS,
    COLLEGE_COMPARISON,
    EXAMPLE_MODULE,
)


class ModuleSelectionResult(BaseModel):
    """Prepared module selection metadata for an orchestrator state."""

    selected_modules: list[str] = Field(default_factory=list)
    unavailable_modules: list[str] = Field(default_factory=list)
    invalid_modules: list[str] = Field(default_factory=list)


class ModuleSelector:
    """Validates target modules and optionally checks registry availability."""

    def __init__(self, registry: ModuleRegistry | None = None) -> None:
        self.registry = registry

    def select(self, intent_result: IntentResult) -> ModuleSelectionResult:
        """Prepare selected modules from an intent result without executing anything."""
        selected_modules: list[str] = []
        unavailable_modules: list[str] = []
        invalid_modules: list[str] = []

        for module_name in intent_result.target_modules:
            if module_name not in OFFICIAL_MODULES:
                invalid_modules.append(module_name)
                continue
            if self.registry is not None and not self.registry.exists(module_name):
                unavailable_modules.append(module_name)
            if module_name not in selected_modules:
                selected_modules.append(module_name)

        return ModuleSelectionResult(
            selected_modules=selected_modules,
            unavailable_modules=unavailable_modules,
            invalid_modules=invalid_modules,
        )
