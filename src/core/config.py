from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """Application settings."""
    # Application Settings
    APP_NAME: str = "Chaysh"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Search Settings
    MAX_SEARCH_RESULTS: int = 10
    CACHE_TTL: int = 3600  # 1 hour

    # Database settings
    DATABASE_URL: str = "sqlite:///./chaysh.db"
    
    # API settings
    API_PREFIX: str = "/api"
    API_VERSION: str = "v1"
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # OpenRouter API settings
    OPENROUTER_API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_API_URL: str = "https://openrouter.ai/api/v1/chat/completions"
    
    # Language settings
    DEFAULT_LANGUAGE: str = "en"
    SUPPORTED_LANGUAGES: list = ["en", "pl"]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Log all environment variables (excluding sensitive ones)
        logger.info("Environment variables loaded:")
        logger.info(f"DEBUG: {self.DEBUG}")
        logger.info(f"LOG_LEVEL: {self.LOG_LEVEL}")
        logger.info(f"API_PREFIX: {self.API_PREFIX}")
        logger.info(f"API_VERSION: {self.API_VERSION}")
        logger.info(f"OPENROUTER_API_URL: {self.OPENROUTER_API_URL}")
        
        if not self.OPENROUTER_API_KEY:
            logger.error("OpenRouter API key not found in environment variables")
            logger.error("Please set OPENROUTER_API_KEY in your environment or .env file")
        else:
            logger.info("OpenRouter API key loaded successfully")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    settings = Settings()
    logger.info(f"Settings loaded with DEBUG={settings.DEBUG}")
    return settings 