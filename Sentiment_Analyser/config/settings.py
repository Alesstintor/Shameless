"""
Application settings and configuration management.

Uses pydantic for validation and environment variable loading.
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Project paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = PROJECT_ROOT / "Sentiment_Analyser" / "data"
    MODELS_DIR: Path = DATA_DIR / "models"
    RAW_DATA_DIR: Path = DATA_DIR / "raw"
    PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"
    
    # Twitter API v2 authentication settings (for tweepy)
    # These must be set in your .env file once you get them from the developer portal
    TWITTER_API_KEY: Optional[str] = None
    TWITTER_API_KEY_SECRET: Optional[str] = None
    TWITTER_ACCESS_TOKEN: Optional[str] = None
    TWITTER_ACCESS_TOKEN_SECRET: Optional[str] = None

    # Bluesky authentication settings (for atproto)
    BLUESKY_HANDLE: Optional[str] = None
    BLUESKY_PASSWORD: Optional[str] = None
    
    # ML Model settings
    MODEL_NAME: str = "distilbert-base-uncased-finetuned-sst-2-english"
    MODEL_MAX_LENGTH: int = 512
    MODEL_BATCH_SIZE: int = 32
    MODEL_DEVICE: str = "cpu"  # or "cuda" if GPU available
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./sentiment_analyser.db"
    DATABASE_ECHO: bool = False
    
    # API settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4
    API_RELOAD: bool = True
    API_DEBUG: bool = True
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DIR: Path = PROJECT_ROOT / "logs"
    
    # Cache settings
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 3600  # seconds
    REDIS_URL: Optional[str] = None

    # External REST API base for precomputed analysis (optional)
    EXTERNAL_ANALYSIS_API_BASE: Optional[str] = None
    
    # Security
    SECRET_KEY: str = "changeme-in-production"
    API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Create necessary directories
def init_directories():
    """Initialize project directories."""
    settings = get_settings()
    directories = [
        settings.DATA_DIR,
        settings.MODELS_DIR,
        settings.RAW_DATA_DIR,
        settings.PROCESSED_DATA_DIR,
        settings.LOG_DIR,
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    # Initialize directories when settings are loaded
    init_directories()
