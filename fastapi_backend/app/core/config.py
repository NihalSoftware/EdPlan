from functools import lru_cache
from typing import List, Union

from pydantic import AnyHttpUrl, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

    app_name: str = Field("Northern New Mexico College Student Hub API", alias="APP_NAME")
    api_prefix: str = Field("/api", alias="API_V1_PREFIX")
    environment: str = Field("development", alias="ENVIRONMENT")
    debug: bool = Field(True, alias="DEBUG")
    host: str = Field("0.0.0.0", alias="HOST")
    port: int = Field(8000, alias="PORT")

    disable_database: bool = Field(False, alias="DISABLE_DATABASE")
    database_url: str = Field(..., alias="DATABASE_URL")

    jwt_secret: str = Field(..., alias="JWT_SECRET")
    jwt_algorithm: str = Field("HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(60, alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    cors_origins: List[AnyHttpUrl] | List[str] = Field(default_factory=list, alias="CORS_ORIGINS")

    smtp_host: str | None = Field(None, alias="SMTP_HOST")
    smtp_port: int | None = Field(None, alias="SMTP_PORT")
    smtp_username: str | None = Field(None, alias="SMTP_USERNAME")
    smtp_password: str | None = Field(None, alias="SMTP_PASSWORD")
    smtp_from_email: str | None = Field("edplan000@gmail.com", alias="SMTP_FROM_EMAIL")
    smtp_from_name: str | None = Field(None, alias="SMTP_FROM_NAME")

    twilio_account_sid: str | None = Field(None, alias="TWILIO_ACCOUNT_SID")
    twilio_auth_token: str | None = Field(None, alias="TWILIO_AUTH_TOKEN")
    twilio_from_number: str | None = Field(None, alias="TWILIO_FROM_NUMBER")

    college_scorecard_api_key: str = Field(..., alias="COLLEGE_SCORECARD_API_KEY")
    college_scorecard_base_url: str = Field(
        "https://api.data.gov/ed/collegescorecard/v1",
        alias="COLLEGE_SCORECARD_BASE_URL",
    )
    openrouter_api_key: SecretStr | None = Field(None, alias="OPENROUTER_API_KEY")
    openrouter_model: str = Field("qwen/qwen3-7b-plus", alias="OPENROUTER_MODEL")
    openrouter_fallback_model: str | None = Field(None, alias="OPENROUTER_FALLBACK_MODEL")
    openrouter_base_url: str = Field(
        "https://openrouter.ai/api/v1",
        alias="OPENROUTER_BASE_URL",
    )
    openrouter_temperature: float = Field(0.2, alias="OPENROUTER_TEMPERATURE")
    openrouter_max_tokens: int = Field(1024, alias="OPENROUTER_MAX_TOKENS")
    openrouter_timeout: float = Field(30.0, alias="OPENROUTER_TIMEOUT")
    default_admin_email: str = Field(..., alias="DEFAULT_ADMIN_EMAIL")
    default_admin_password: str = Field(..., alias="DEFAULT_ADMIN_PASSWORD")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_origins(cls, value: Union[str, List[AnyHttpUrl], List[str]]) -> Union[List[AnyHttpUrl], List[str]]:  # type: ignore[override]
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if not isinstance(value, str):
            return value

        url = value.strip()

        # Render and other platforms commonly provide "postgres://" URLs.
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://") :]

        # This app uses SQLAlchemy asyncio; ensure an async driver is selected by default.
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

        return url


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    # Construct Settings without passing constructor args so BaseSettings reads env vars;
    # static type checkers may incorrectly require all fields as constructor args, so ignore that.
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
