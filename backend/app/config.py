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
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "cinecraft"
    vector_provider: str = "memory"
    qdrant_url: str | None = None
    qdrant_api_key: str | None = None
    embedding_dimension: int = 128
    cors_origins: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
