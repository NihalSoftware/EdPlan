from __future__ import annotations

from typing import Any

from app.orchestrator.llm.base_provider import BaseLLMProvider, StructuredOutput
from app.orchestrator.llm.llm_models import LLMHealthCheck, LLMRequest, LLMResponse, LLMUsage
from app.orchestrator.llm.model_config import LLMModelConfig


class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter-compatible provider stub.

    This class prepares request/response architecture only. It does not make
    network calls, read API keys, or connect to OpenRouter.
    """

    provider_name = "openrouter"

    def __init__(self, model_config: LLMModelConfig | None = None) -> None:
        self.model_config = model_config or LLMModelConfig()

    async def generate(self, request: LLMRequest) -> LLMResponse:
        payload = self.build_request_payload(request)
        return self.parse_response(
            {
                "model": payload["model"],
                "choices": [
                    {
                        "message": {
                            "content": "",
                        },
                        "finish_reason": "stubbed",
                    }
                ],
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                },
                "metadata": {
                    "stub": True,
                    "provider": self.provider_name,
                },
            }
        )

    async def generate_structured(
        self,
        request: LLMRequest,
        response_model: type[StructuredOutput],
    ) -> StructuredOutput:
        await self.generate(request)
        return response_model.model_validate({})

    async def health_check(self) -> LLMHealthCheck:
        return LLMHealthCheck(
            provider=self.provider_name,
            ok=True,
            message="OpenRouter provider stub is configured. Network calls are disabled.",
            metadata={"network_enabled": False},
        )

    def build_request_payload(self, request: LLMRequest) -> dict[str, Any]:
        messages = [message.model_dump(mode="json") for message in request.messages]
        if request.system_prompt:
            messages = [{"role": "system", "content": request.system_prompt, "metadata": {}}] + messages

        return {
            "model": request.model or self.model_config.primary_model,
            "messages": messages,
            "temperature": (
                request.temperature
                if request.temperature is not None
                else self.model_config.temperature
            ),
            "max_tokens": (
                request.max_tokens if request.max_tokens is not None else self.model_config.max_tokens
            ),
            "metadata": request.metadata,
        }

    @staticmethod
    def parse_response(raw_response: dict[str, Any]) -> LLMResponse:
        choices = raw_response.get("choices") or []
        first_choice = choices[0] if choices else {}
        message = first_choice.get("message") or {}
        usage = raw_response.get("usage")

        return LLMResponse(
            model=str(raw_response.get("model", "")),
            content=str(message.get("content", "")),
            metadata=dict(raw_response.get("metadata") or {}),
            usage=LLMUsage.model_validate(usage) if usage is not None else None,
            finish_reason=first_choice.get("finish_reason"),
            raw_response=raw_response,
        )
