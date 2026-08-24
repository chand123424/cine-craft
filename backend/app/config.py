from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    grok_api_key: str | None = None
    google_ai_api_key: str | None = None
    huggingface_api_key: str | None = None
    ai_provider: str = "mock"
    ai_model: str | None = None
    request_timeout_seconds: float = 30.0
    
    ai_max_retries: int = 2

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
