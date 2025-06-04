from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application settings."""
    # API Configuration
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gpt-4-mini")
    
    # Application Settings
    APP_NAME: str = "Chaysh"
    DEBUG: bool = False
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Search Settings
    MAX_SEARCH_RESULTS: int = 10
    CACHE_TTL: int = 3600  # 1 hour
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings() 