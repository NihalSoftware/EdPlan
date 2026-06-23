from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class LLMModelConfig(BaseModel):
    """Central model configuration for provider-independent LLM usage."""

    primary_model: str = Field("configured-primary-model", min_length=1)
    fallback_model: str | None = Field("configured-fallback-model")
    temperature: float = Field(0.2, ge=0.0, le=2.0)
    max_tokens: int = Field(1024, gt=0)
    timeout: float = Field(30.0, gt=0)

    @field_validator("primary_model", "fallback_model")
    @classmethod
    def normalize_model_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("model name cannot be blank")
        return normalized
