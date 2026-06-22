from __future__ import annotations

import pytest
from pydantic import BaseModel

from app.orchestrator.llm import (
    BaseLLMProvider,
    LLMMessage,
    LLMModelConfig,
    LLMRequest,
    LLMResponse,
    OpenRouterProvider,
    PromptCategory,
    PromptManager,
    PromptRegistry,
    PromptTemplate,
)
from app.orchestrator.services.student_orchestrator import StudentOrchestrator


class EmptyStructuredResponse(BaseModel):
    pass


def test_base_provider_is_abstract():
    with pytest.raises(TypeError):
        BaseLLMProvider()  # type: ignore[abstract]


def test_model_configuration_is_centralized_and_configurable():
    config = LLMModelConfig(
        primary_model="provider/model-a",
        fallback_model="provider/model-b",
        temperature=0.4,
        max_tokens=2048,
        timeout=45.0,
    )

    assert config.primary_model == "provider/model-a"
    assert config.fallback_model == "provider/model-b"
    assert config.temperature == 0.4
    assert config.max_tokens == 2048
    assert config.timeout == 45.0


def test_prompt_manager_renders_registered_prompt():
    registry = PromptRegistry(
        [
            PromptTemplate(
                name="test.prompt",
                category=PromptCategory.INTENT_ROUTING,
                template="Route: {query}",
                required_variables={"query"},
            )
        ]
    )

    rendered = PromptManager(registry).render("test.prompt", {"query": "Plan my courses"})

    assert rendered == "Route: Plan my courses"


def test_prompt_manager_validates_required_variables():
    manager = PromptManager(
        PromptRegistry(
            [
                PromptTemplate(
                    name="test.prompt",
                    category=PromptCategory.RESPONSE_GENERATION,
                    template="Respond to {query}",
                    required_variables={"query"},
                )
            ]
        )
    )

    with pytest.raises(ValueError, match="missing variables"):
        manager.render("test.prompt", {})


def test_prompt_registry_contains_future_categories():
    registry = PromptRegistry()

    assert registry.list_by_category(PromptCategory.INTENT_ROUTING)
    assert registry.list_by_category(PromptCategory.MEMORY_SUMMARIZATION)
    assert registry.list_by_category(PromptCategory.RESPONSE_GENERATION)
    assert registry.list_by_category(PromptCategory.ACADEMIC_PLANNING)
    assert registry.list_by_category(PromptCategory.SCHEDULING)
    assert registry.list_by_category(PromptCategory.CAREER_GUIDANCE)
    assert registry.list_by_category(PromptCategory.FINANCE_GUIDANCE)
    assert registry.list_by_category(PromptCategory.ACADEMIC_SUCCESS)
    assert registry.list_by_category(PromptCategory.COLLEGE_COMPARISON)


def test_llm_request_response_serialization():
    request = LLMRequest(
        model="provider/model",
        system_prompt="System",
        messages=[LLMMessage(role="user", content="Hello")],
        metadata={"purpose": "test"},
    )
    response = LLMResponse(
        model="provider/model",
        content="Hello back",
        finish_reason="stop",
        metadata={"stub": True},
    )

    assert request.model_dump(mode="json")["messages"][0]["role"] == "user"
    assert response.model_dump(mode="json")["finish_reason"] == "stop"


def test_openrouter_provider_builds_request_payload_without_network():
    provider = OpenRouterProvider(LLMModelConfig(primary_model="configured/model"))
    request = LLMRequest(
        system_prompt="System",
        messages=[LLMMessage(role="user", content="Hello")],
    )

    payload = provider.build_request_payload(request)

    assert payload["model"] == "configured/model"
    assert payload["messages"][0]["role"] == "system"
    assert payload["messages"][1]["content"] == "Hello"


@pytest.mark.asyncio
async def test_openrouter_provider_returns_stub_response():
    provider = OpenRouterProvider(LLMModelConfig(primary_model="configured/model"))

    response = await provider.generate(
        LLMRequest(messages=[LLMMessage(role="user", content="Hello")])
    )
    health = await provider.health_check()
    structured = await provider.generate_structured(
        LLMRequest(messages=[LLMMessage(role="user", content="Return json")]),
        EmptyStructuredResponse,
    )

    assert response.model == "configured/model"
    assert response.metadata["stub"] is True
    assert health.ok is True
    assert health.metadata["network_enabled"] is False
    assert isinstance(structured, EmptyStructuredResponse)


def test_student_orchestrator_accepts_llm_provider_without_using_it():
    provider = OpenRouterProvider()

    orchestrator = StudentOrchestrator(llm_provider=provider)

    assert orchestrator.llm_provider is provider
