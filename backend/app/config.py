from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Web Research MCP"
    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@postgres:5432/web_research"
    )
    ollama_base_url: str = "https://ollama.com/api"
    ollama_api_key: str = ""
    ollama_model: str = "llama3"
    frontend_origin: str = "http://localhost:5173"


@lru_cache
def get_settings() -> Settings:
    return Settings()
