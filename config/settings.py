"""
Configuration Settings for TradeMate Bot
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # Deriv API
    DERIV_API_TOKEN: str
    DERIV_APP_ID: str = "1089"

    # Account
    DEMO_MODE: bool = True
    INITIAL_STAKE: float = 10.0

    # Trading
    TRADING_SYMBOL: str = "R_100"
    CANDLE_INTERVAL: int = 300
    MIN_CONFIRMATIONS: int = 3

    # Risk Management
    RISK_PER_TRADE: float = 0.02
    MAX_DAILY_LOSS: float = 0.05
    MAX_CONSECUTIVE_LOSSES: int = 3
    MAX_TRADES_PER_DAY: int = 10
    MIN_RISK_REWARD_RATIO: float = 1.5

    # Strategy
    EMA_FAST: int = 50
    EMA_SLOW: int = 200
    RSI_PERIOD: int = 14
    RSI_OVERSOLD: int = 30
    RSI_OVERBOUGHT: int = 70

    # Telegram (optional)
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/trademate.log"

    # Environment
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()


# Create logs directory
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Create data directory
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)
