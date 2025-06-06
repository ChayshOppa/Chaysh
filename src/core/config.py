from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings."""
    # Application Settings
    APP_NAME: str = "Chaysh"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Search Settings
    MAX_SEARCH_RESULTS: int = 10
    CACHE_TTL: int = 3600  # 1 hour

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings() 