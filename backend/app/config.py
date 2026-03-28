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
    ollama_model: str = "gpt-oss:120b"
    alpha_vantage_api_key: str = ""
    frontend_origin: str = "http://localhost:5173"
    frontend_url: str = "http://localhost:5173"
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_cookie_name: str = "auth_token"
    auth_token_ttl_days: int = 7
    cookie_secure: bool = False
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/auth/google/callback"
    google_oauth_state_cookie: str = "google_oauth_state"


@lru_cache
def get_settings() -> Settings:
    return Settings()
