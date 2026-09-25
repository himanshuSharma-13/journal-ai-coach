from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://journal:journal@localhost:5433/journal_ai"
    cors_origins: str = "http://localhost:3000"
    jwt_secret: str = "development-only-secret-change-me"
    jwt_algorithm: str = "HS256"
    groq_api_key: Optional[str] = None
    groq_insight_model: str = "openai/gpt-oss-20b"
    openai_api_key: Optional[str] = None
    openai_embedding_model: str = "text-embedding-3-small"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
