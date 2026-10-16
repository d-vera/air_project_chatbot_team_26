import os
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    jwt_secret: str = Field(..., alias="JWT_SECRET", description="Secret used to validate JWT tokens")
    upstream_api_url: str = Field("http://localhost:8080", alias="UPSTREAM_API_URL")
    deepseek_api_key: str = Field("", alias="DEEPSEEK_API_KEY")
    llm_api_key: str = Field("", alias="LLM_API_KEY")
    openai_api_key: str = Field("", alias="OPENAI_API_KEY")
    llm_base_url: str = Field("https://api.deepseek.com", alias="LLM_BASE_URL")
    llm_model: str = Field("deepseek-chat", alias="LLM_MODEL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("JWT_SECRET must be set and non-empty")
        return v.strip()

    @property
    def effective_llm_api_key(self) -> str:
        return (
            self.deepseek_api_key
            or self.llm_api_key
            or self.openai_api_key
            or os.getenv("DEEPSEEK_API_KEY", "")
            or os.getenv("OPENAI_API_KEY", "")
        )


def get_settings() -> Settings:
    return Settings()
