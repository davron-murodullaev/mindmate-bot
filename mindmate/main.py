"""
MindMate Telegram Bot - Main Entry Point

This is the central entry point for the MindMate bot using a modular architecture.
It initializes the bot using python-telegram-bot v22.5 and registers all handlers.
"""

import os
import asyncio
from telegram.ext import ApplicationBuilder

from mindmate.handlers.start import register_start_handlers
from mindmate.handlers.menu import register_menu_handlers
from mindmate.handlers.mood import register_mood_handlers
from mindmate.handlers.meditation import register_meditation_handlers
from mindmate.handlers.journal import register_journal_handlers
from mindmate.handlers.fitness import register_fitness_handlers
from mindmate.handlers.healer import register_healer_handlers
from mindmate.handlers.stats import register_stats_handlers
from mindmate.handlers.productivity import register_productivity_handlers
from mindmate.handlers.finance import register_finance_handlers


async def run_bot():
    """
    Initialize and run the MindMate Telegram bot.

    Loads the bot token from environment variables and registers all handlers
    before starting the polling loop.
    """
    # Load bot token from environment
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token:
        raise ValueError(
            "TELEGRAM_BOT_TOKEN environment variable is not set. "
            "Please set it in your .env file or environment."
        )

    # Build the application
    app = ApplicationBuilder().token(token).build()

    # Register all handlers in order
    register_start_handlers(app)
    register_menu_handlers(app)
    register_mood_handlers(app)
    register_meditation_handlers(app)
    register_journal_handlers(app)
    register_fitness_handlers(app)
    register_healer_handlers(app)
    register_stats_handlers(app)
    register_productivity_handlers(app)
    register_finance_handlers(app)

    print("✨ MindMate bot is running...")
    print("Press Ctrl+C to stop")

    # Start polling for updates
    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(run_bot())
