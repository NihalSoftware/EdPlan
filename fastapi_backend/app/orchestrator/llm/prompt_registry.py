from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class PromptCategory(str, Enum):
    INTENT_ROUTING = "intent_routing"
    MEMORY_SUMMARIZATION = "memory_summarization"
    RESPONSE_GENERATION = "response_generation"
    ACADEMIC_PLANNING = "academic_planning"
    SCHEDULING = "scheduling"
    CAREER_GUIDANCE = "career_guidance"
    FINANCE_GUIDANCE = "finance_guidance"
    ACADEMIC_SUCCESS = "academic_success"
    COLLEGE_COMPARISON = "college_comparison"


class PromptTemplate(BaseModel):
    """Registered prompt template metadata."""

    name: str = Field(..., min_length=1)
    category: PromptCategory
    template: str = Field(..., min_length=1)
    description: str | None = None
    required_variables: set[str] = Field(default_factory=set)


class PromptRegistry:
    """In-memory registry for future orchestrator prompt templates."""

    def __init__(self, prompts: list[PromptTemplate] | None = None) -> None:
        self._prompts: dict[str, PromptTemplate] = {}
        for prompt in prompts or default_prompt_templates():
            self.register(prompt)

    def register(self, prompt: PromptTemplate) -> None:
        if prompt.name in self._prompts:
            raise ValueError(f"Prompt already registered: {prompt.name}")
        self._prompts[prompt.name] = prompt

    def get(self, name: str) -> PromptTemplate:
        try:
            return self._prompts[name]
        except KeyError as exc:
            raise KeyError(f"Prompt is not registered: {name}") from exc

    def list_by_category(self, category: PromptCategory) -> list[PromptTemplate]:
        return [prompt for prompt in self._prompts.values() if prompt.category == category]

    def list_names(self) -> list[str]:
        return sorted(self._prompts)


def default_prompt_templates() -> list[PromptTemplate]:
    return [
        PromptTemplate(
            name="intent_routing.default",
            category=PromptCategory.INTENT_ROUTING,
            template="Classify the student request: {query}",
            required_variables={"query"},
        ),
        PromptTemplate(
            name="memory_summarization.default",
            category=PromptCategory.MEMORY_SUMMARIZATION,
            template="Summarize durable student preferences from: {conversation}",
            required_variables={"conversation"},
        ),
        PromptTemplate(
            name="response_generation.default",
            category=PromptCategory.RESPONSE_GENERATION,
            template="Compose a concise response for: {query}",
            required_variables={"query"},
        ),
        PromptTemplate(
            name="academic_planning.default",
            category=PromptCategory.ACADEMIC_PLANNING,
            template="Academic planning context: {context}",
            required_variables={"context"},
        ),
        PromptTemplate(
            name="scheduling.default",
            category=PromptCategory.SCHEDULING,
            template="Scheduling context: {context}",
            required_variables={"context"},
        ),
        PromptTemplate(
            name="career_guidance.default",
            category=PromptCategory.CAREER_GUIDANCE,
            template="Career guidance context: {context}",
            required_variables={"context"},
        ),
        PromptTemplate(
            name="finance_guidance.default",
            category=PromptCategory.FINANCE_GUIDANCE,
            template="Finance guidance context: {context}",
            required_variables={"context"},
        ),
        PromptTemplate(
            name="academic_success.default",
            category=PromptCategory.ACADEMIC_SUCCESS,
            template="Academic success context: {context}",
            required_variables={"context"},
        ),
        PromptTemplate(
            name="college_comparison.default",
            category=PromptCategory.COLLEGE_COMPARISON,
            template="College comparison context: {context}",
            required_variables={"context"},
        ),
    ]
