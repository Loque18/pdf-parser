from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "API Service"
    app_version: str = "0.1.0"
    database_url: str = "sqlite:///./app.db"
    redis_url: str = "redis://localhost:6379/0"
    job_queue_enabled: bool = False
    llama_api_key: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
