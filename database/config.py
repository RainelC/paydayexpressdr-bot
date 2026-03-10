"""Application settings loaded from environment / .env file."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Twilio credentials
    twilio_account_sid: str = "TWILIO_ACCOUNT_SID"
    twilio_auth_token: str = "TWILIO_AUTH_TOKEN"
    twilio_whatsapp_from: str = "whatsapp:+14155238886"

    # Database (defaults to async SQLite for development)
    database_url: str = "sqlite+aiosqlite:///./bot.db"

    # Application
    debug: bool = False
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
