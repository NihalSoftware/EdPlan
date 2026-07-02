from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel, Field, field_validator
from pydantic import SecretStr


class LLMModelConfig(BaseModel):
    """Central model configuration for provider-independent LLM usage."""

    primary_model: str = Field("qwen/qwen3.7-plus", min_length=1)
    fallback_model: str | None = None
    temperature: float = Field(0.2, ge=0.0, le=2.0)
    max_tokens: int = Field(1024, gt=0)
    timeout: float = Field(30.0, gt=0)
    api_base_url: str = Field("https://openrouter.ai/api/v1", min_length=1)
    api_key: SecretStr | None = Field(default=None, exclude=True)
    reasoning_enabled: bool = False

    @classmethod
    def from_env(cls) -> "LLMModelConfig":
        """Build model config from environment variables without requiring app settings."""
        env_file = _read_dotenv()
        return cls(
            primary_model=_env_value(env_file, "OPENROUTER_MODEL", "qwen/qwen3.7-plus"),
            fallback_model=_env_value(env_file, "OPENROUTER_FALLBACK_MODEL") or None,
            temperature=float(_env_value(env_file, "OPENROUTER_TEMPERATURE", "0.2")),
            max_tokens=int(_env_value(env_file, "OPENROUTER_MAX_TOKENS", "1024")),
            timeout=float(_env_value(env_file, "OPENROUTER_TIMEOUT", "30")),
            api_base_url=_env_value(
                env_file,
                "OPENROUTER_BASE_URL",
                "https://openrouter.ai/api/v1",
            ),
            api_key=_env_value(env_file, "OPENROUTER_API_KEY") or None,
            reasoning_enabled=_env_bool(env_file, "OPENROUTER_REASONING_ENABLED", False),
        )

    @field_validator("primary_model", "fallback_model")
    @classmethod
    def normalize_model_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("model name cannot be blank")
        return normalized


def _env_value(dotenv: dict[str, str], key: str, default: str | None = None) -> str | None:
    value = os.getenv(key)
    if value is not None:
        return value
    return dotenv.get(key, default)


def _read_dotenv() -> dict[str, str]:
    for directory in [Path.cwd(), *Path.cwd().parents]:
        env_path = directory / ".env"
        if env_path.is_file():
            return _parse_dotenv(env_path)
    return {}


def _env_bool(dotenv: dict[str, str], key: str, default: bool) -> bool:
    value = _env_value(dotenv, key)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_dotenv(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return values
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value
    return values

    @field_validator("api_base_url")
    @classmethod
    def normalize_api_base_url(cls, value: str) -> str:
        normalized = value.strip().rstrip("/")
        if not normalized:
            raise ValueError("api_base_url cannot be blank")
        return normalized
