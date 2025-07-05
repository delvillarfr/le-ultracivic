from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = Field(..., description="PostgreSQL database URL")
    debug: bool = Field(default=False, description="Enable debug mode")


settings = Settings()