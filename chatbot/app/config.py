import os
import subprocess
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _read_keychain(service: str, account: str | None = None) -> str:
    """Retrieve a generic password from macOS Keychain."""
    account = account or os.environ.get("USER", "")
    if account:
        try:
            result = subprocess.run(
                ["security", "find-generic-password", "-a", account, "-s", service, "-w"],
                capture_output=True,
                text=True,
                check=True,
            )
            val = result.stdout.strip()
            if val:
                return val
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", service, "-w"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


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
        # Check environment variables and .env
        for candidate in (
            self.deepseek_api_key,
            self.llm_api_key,
            self.openai_api_key,
            os.getenv("DEEPSEEK_API_KEY", ""),
            os.getenv("LLM_API_KEY", ""),
            os.getenv("OPENAI_API_KEY", ""),
        ):
            val = candidate.strip() if candidate else ""
            if val and val not in ("your_deepseek_api_key_here", "your_api_key_here", "<DEEPSEEK_API_KEY>"):
                return val

        # Fallback to macOS Keychain
        return _read_keychain("DEEPSEEK_API_KEY") or _read_keychain("LLM_API_KEY")


def get_settings() -> Settings:
    return Settings()
