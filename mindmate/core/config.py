"""
Configuration management using Pydantic Settings
"""
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""

    # Bot Configuration
    TELEGRAM_BOT_TOKEN: str = Field(..., description="Telegram Bot API Token")
    ADMIN_USER_IDS: str = Field(default="", description="Comma-separated admin user IDs")

    # AI Configuration
    ANTHROPIC_API_KEY: str = Field(..., description="Anthropic API Key for Claude")
    AI_MODEL: str = Field(default="claude-3-5-sonnet-20241022", description="AI model to use")
    MAX_TOKENS: int = Field(default=2048, description="Maximum tokens for AI responses")
    TEMPERATURE: float = Field(default=0.7, description="AI temperature setting")

    # Database Configuration
    DATABASE_URL: str = Field(..., description="PostgreSQL database URL")
    DB_POOL_MIN_SIZE: int = Field(default=5, description="Minimum database pool size")
    DB_POOL_MAX_SIZE: int = Field(default=20, description="Maximum database pool size")

    # Application Settings
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    ENVIRONMENT: str = Field(default="production", description="Environment (development/production)")
    DEBUG: bool = Field(default=False, description="Debug mode")

    # Feature Flags
    ENABLE_REMINDERS: bool = Field(default=True, description="Enable reminder system")
    ENABLE_ANALYTICS: bool = Field(default=True, description="Enable analytics tracking")

    # Reminder Settings
    REMINDER_CHECK_INTERVAL: int = Field(default=60, description="Reminder check interval in seconds")

    # Timezone
    TIMEZONE: str = Field(default="UTC", description="Default timezone")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @property
    def admin_user_ids_list(self) -> List[int]:
        """Get admin user IDs as a list of integers."""
        if not self.ADMIN_USER_IDS:
            return []
        return [int(uid.strip()) for uid in self.ADMIN_USER_IDS.split(",") if uid.strip()]

    def is_admin(self, user_id: int) -> bool:
        """Check if a user is an admin."""
        return user_id in self.admin_user_ids_list


# Global settings instance
settings = Settings()
