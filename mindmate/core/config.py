"""
Configuration management using Pydantic Settings
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""

    # ── Bot Configuration ────────────────────────────────────────────
    TELEGRAM_BOT_TOKEN: str = Field(..., description="Telegram Bot API Token")
    ADMIN_USER_IDS: str = Field(default="", description="Comma-separated admin user IDs")

    # ── AI Provider Selection ────────────────────────────────────────
    # "openai" or "anthropic". Switch by changing this single env var.
    AI_PROVIDER: str = Field(default="openai", description="Which AI provider to use")

    # OpenAI (ChatGPT)
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API Key")
    OPENAI_MODEL: str = Field(default="gpt-4o-mini", description="OpenAI model")

    # Anthropic (Claude)
    ANTHROPIC_API_KEY: str = Field(default="", description="Anthropic API Key for Claude")
    ANTHROPIC_MODEL: str = Field(default="claude-sonnet-4-5", description="Anthropic model")

    # Shared AI generation settings
    MAX_TOKENS: int = Field(default=2048, description="Maximum tokens for AI responses")
    TEMPERATURE: float = Field(default=0.7, description="AI temperature setting")

    # ── Database Configuration ───────────────────────────────────────
    DATABASE_URL: str = Field(..., description="PostgreSQL database URL")
    DB_POOL_MIN_SIZE: int = Field(default=5, description="Minimum database pool size")
    DB_POOL_MAX_SIZE: int = Field(default=20, description="Maximum database pool size")

    # ── Application Settings ─────────────────────────────────────────
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    ENVIRONMENT: str = Field(default="production", description="Environment")
    DEBUG: bool = Field(default=False, description="Debug mode")

    # ── Feature Flags ────────────────────────────────────────────────
    ENABLE_REMINDERS: bool = Field(default=True, description="Enable reminder system")
    ENABLE_ANALYTICS: bool = Field(default=True, description="Enable analytics tracking")

    # ── Reminder Settings ────────────────────────────────────────────
    REMINDER_CHECK_INTERVAL: int = Field(default=60, description="Reminder check interval (s)")

    # ── Timezone ─────────────────────────────────────────────────────
    TIMEZONE: str = Field(default="UTC", description="Default timezone")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
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

    # ── Convenience: which provider is active ────────────────────────
    @property
    def active_provider(self) -> str:
        return (self.AI_PROVIDER or "openai").lower()

    @property
    def active_model(self) -> str:
        if self.active_provider == "anthropic":
            return self.ANTHROPIC_MODEL
        return self.OPENAI_MODEL


# Global settings instance
settings = Settings()
