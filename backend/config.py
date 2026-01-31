"""Configuration settings for the Movie Argument Engine."""

from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    tmdb_api_key: str = os.getenv("TMDB_API_KEY", "")
    
    # API URLs
    tmdb_base_url: str = "https://api.themoviedb.org/3"
    tmdb_image_base_url: str = "https://image.tmdb.org/t/p"
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./movie_cache.db"
    cache_ttl_hours: int = 24
    
    # Scoring Defaults
    default_weights: dict = {
        "vote_average": 0.25,
        "vote_count": 0.15,
        "popularity": 0.20,
        "revenue": 0.10,
        "runtime_quality": 0.05,
        "release_recency": 0.10,
        "cast_star_power": 0.15,
    }
    
    # App Settings
    app_name: str = "Movie Argument Engine"
    debug: bool = True
    cors_origins: list = ["http://localhost:5173", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        extra = "allow"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
