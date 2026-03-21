"""
Configuration management using environment variables.
Uses pydantic-settings for type-safe configuration.
"""

from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    environment: str = "development"

    # Restaurant Information
    restaurant_name: str = "The Common House"

    # AI Model (Optional - for future llama.cpp integration)
    llama_server_url: Optional[str] = None
    use_local_ai: bool = False

    # Security
    secret_key: str = "dev-secret-key-change-in-production"

    # CORS
    allowed_origins: str = "*"  # Comma-separated list

    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/app.log"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")

    @property
    def allowed_origins_list(self) -> list[str]:
        """Convert comma-separated CORS origins to list."""
        if self.allowed_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment.lower() == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment.lower() == "production"


# Create global settings instance
settings = Settings()


# Ensure required directories exist
def ensure_directories():
    """Create necessary directories if they don't exist."""
    base_dir = Path(__file__).parent.parent

    directories = [
        base_dir / "data",
        base_dir / "logs",
        base_dir / "models",
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


# Run on import
ensure_directories()
