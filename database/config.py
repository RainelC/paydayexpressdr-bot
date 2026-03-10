"""Application settings loaded from environment / .env file."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Meta WhatsApp Business API credentials
    whatsapp_api_token: str = "WHATSAPP_API_TOKEN"
    whatsapp_phone_number_id: str = "WHATSAPP_PHONE_NUMBER_ID"
    whatsapp_verify_token: str = "WHATSAPP_VERIFY_TOKEN"

    # Database (defaults to async SQLite for development)
    database_url: str = "sqlite+aiosqlite:///./bot.db"

    # Application
    debug: bool = False
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
