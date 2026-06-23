from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, TypeVar

from pydantic import BaseModel

from app.orchestrator.llm.llm_models import LLMHealthCheck, LLMRequest, LLMResponse

StructuredOutput = TypeVar("StructuredOutput", bound=BaseModel)


class BaseLLMProvider(ABC):
    """Abstract interface implemented by future LLM providers."""

    provider_name: str

    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a provider-neutral text response."""

    @abstractmethod
    async def generate_structured(
        self,
        request: LLMRequest,
        response_model: type[StructuredOutput],
    ) -> StructuredOutput:
        """Generate and parse a structured response."""

    @abstractmethod
    async def health_check(self) -> LLMHealthCheck:
        """Return provider health without leaking provider implementation details."""


class LLMProviderError(RuntimeError):
    """Raised when an LLM provider cannot satisfy a request."""

    def __init__(self, message: str, *, metadata: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.metadata = metadata or {}
