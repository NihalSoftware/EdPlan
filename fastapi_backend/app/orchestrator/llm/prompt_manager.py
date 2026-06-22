from __future__ import annotations

from string import Formatter
from typing import Any

from app.orchestrator.llm.prompt_registry import PromptRegistry, PromptTemplate


class PromptManager:
    """Loads, validates, and renders registered prompt templates."""

    def __init__(self, registry: PromptRegistry | None = None) -> None:
        self.registry = registry or PromptRegistry()

    def load_prompt(self, name: str) -> PromptTemplate:
        return self.registry.get(name)

    def render(self, name: str, variables: dict[str, Any]) -> str:
        prompt = self.load_prompt(name)
        self.validate(prompt, variables)
        safe_variables = {key: str(value) for key, value in variables.items()}
        return prompt.template.format(**safe_variables)

    def validate(self, prompt: PromptTemplate, variables: dict[str, Any]) -> None:
        required_variables = prompt.required_variables or _template_variables(prompt.template)
        missing_variables = sorted(required_variables.difference(variables))
        if missing_variables:
            raise ValueError(
                f"Prompt '{prompt.name}' is missing variables: {', '.join(missing_variables)}"
            )


def _template_variables(template: str) -> set[str]:
    return {
        field_name
        for _, field_name, _, _ in Formatter().parse(template)
        if field_name is not None and field_name
    }
