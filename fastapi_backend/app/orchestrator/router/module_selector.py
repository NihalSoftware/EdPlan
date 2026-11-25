from __future__ import annotations

from pydantic import BaseModel, Field

from app.orchestrator.modules.module_registry import ModuleRegistry
from app.orchestrator.schemas.intent_result import IntentResult

ACADEMIC_PLANNING = "academic_planning"
SCHEDULING = "scheduling"
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
    execution_plan: list[dict[str, object]] = Field(default_factory=list)


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

        selected_modules = _ordered_for_dependencies(selected_modules)
        return ModuleSelectionResult(
            selected_modules=selected_modules,
            unavailable_modules=unavailable_modules,
            invalid_modules=invalid_modules,
            execution_plan=_build_execution_plan(selected_modules),
        )


def _ordered_for_dependencies(modules: list[str]) -> list[str]:
    ordered = list(modules)
    _move_after(ordered, SCHEDULING, ACADEMIC_PLANNING)
    _move_after(ordered, COLLEGE_COMPARISON, ACADEMIC_PLANNING)
    _move_after(ordered, COLLEGE_COMPARISON, SCHEDULING)
    return ordered


def _move_after(modules: list[str], module_name: str, dependency: str) -> None:
    if module_name not in modules or dependency not in modules:
        return
    module_index = modules.index(module_name)
    dependency_index = modules.index(dependency)
    if module_index > dependency_index:
        return
    modules.pop(module_index)
    dependency_index = modules.index(dependency)
    modules.insert(dependency_index + 1, module_name)


def _build_execution_plan(modules: list[str]) -> list[dict[str, object]]:
    plan = []
    for index, module_name in enumerate(modules, start=1):
        depends_on: list[str] = []
        consumes: list[str] = []
        if module_name == SCHEDULING and ACADEMIC_PLANNING in modules:
            depends_on.append(ACADEMIC_PLANNING)
            consumes.append("academic_plan")
        if module_name == COLLEGE_COMPARISON:
            if ACADEMIC_PLANNING in modules:
                depends_on.append(ACADEMIC_PLANNING)
                consumes.append("academic_plan")
            if SCHEDULING in modules:
                depends_on.append(SCHEDULING)
                consumes.append("schedule_plan")
        plan.append(
            {
                "step": index,
                "module_name": module_name,
                "depends_on": depends_on,
                "consumes": consumes,
                "provides": _provides(module_name),
                "continue_on_failure": True,
            }
        )
    return plan


def _provides(module_name: str) -> list[str]:
    if module_name == ACADEMIC_PLANNING:
        return ["academic_plan"]
    if module_name == SCHEDULING:
        return ["schedule_plan"]
    if module_name == COLLEGE_COMPARISON:
        return ["comparison_plan", "recommended_university"]
    return []
