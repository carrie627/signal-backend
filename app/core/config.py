from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    webhook_secret: str
    embedding_model_name: str = "all-MiniLM-L6-v2"

    hot_threshold: int = 80
    warm_threshold: int = 50

    groq_api_key: str = ""
    groq_model: str = "llama-3.1-8b-instant"

    google_service_account_file: str = "service-account.json"
    google_sheet_id: str = ""

    zapier_hot_webhook_url: str = ""
    zapier_default_webhook_url: str = ""


@lru_cache
def get_settings() -> Settings:
    # lru_cache means .env is only read once per process, not per request
    return Settings()
