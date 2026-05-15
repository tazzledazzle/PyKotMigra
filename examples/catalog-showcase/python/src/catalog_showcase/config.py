"""Configuration from environment with defaults (catalog: config)."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False, env_prefix="SHOWCASE_")

    service_name: str = "catalog-showcase"
    downstream_base_url: str | None = None
    api_key: str = "demo-key"


@lru_cache
def get_settings() -> Settings:
    return Settings()
