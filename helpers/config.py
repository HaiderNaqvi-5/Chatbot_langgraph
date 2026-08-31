"""Application settings: one typed object, loaded once from the environment."""

from functools import lru_cache
from typing import Literal
from dotenv import load_dotenv

# Call this before initializing settings or the ChatGroq client
load_dotenv()

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Every knob the app has. Nothing reads os.environ directly except this class."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Chat API"
    environment: Literal["dev", "staging", "prod"] = "dev"
    debug: bool = True
    history_token_budget: int = 3000

    # These are now required to be in the .env file
    database_url: str 
    groq_api_key: str = Field(description="Set GROQ_API_KEY in .env")
    
    # Model config and settings
    groq_model: str 
    groq_temperature: float
    groq_max_tokens: int
    groq_timeout_seconds: float
    
    # System instructions
    system_prompt: str


@lru_cache
def get_settings() -> Settings:
    """Cached so the .env file is parsed exactly once per process."""
    return Settings()


settings = get_settings()