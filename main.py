"""
MindMate Bot - Main Entry Point
"""
import asyncio
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from mindmate.core.config import settings
from mindmate.core.logger import setup_logger
from mindmate.db.connection import init_db
from mindmate.reminders.scheduler import start_scheduler

# Import all handlers
from mindmate.handlers.start import start_handler, language_callback, setup_callback
from mindmate.handlers.menu import menu_handler, main_menu_callback
from mindmate.handlers.mood import mood_handler, mood_callback, save_mood_handler
from mindmate.handlers.meditation import meditation_handler, meditation_callback, meditation_duration_callback
from mindmate.handlers.fitness import fitness_handler, fitness_callback, log_workout_handler
from mindmate.handlers.healer import healer_handler, healer_message_handler
from mindmate.handlers.journal import journal_handler, journal_callback, save_journal_handler
from mindmate.handlers.productivity import productivity_handler, productivity_message_handler
from mindmate.handlers.finance import finance_handler, finance_callback, add_expense_handler
from mindmate.handlers.stats import stats_handler, stats_callback

logger = setup_logger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")


async def post_init(application: Application) -> None:
    """Initialize components after application startup."""
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized successfully")

        # Start reminder scheduler
        await start_scheduler(application.bot)
        logger.info("Reminder scheduler started successfully")

    except Exception as e:
        logger.error(f"Error during post-init: {e}")
        raise


def main():
    """Main function to run the bot."""
    logger.info("Starting MindMate Bot...")

    # Create application
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).post_init(post_init).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("menu", menu_handler))
    application.add_handler(CommandHandler("mood", mood_handler))
    application.add_handler(CommandHandler("meditation", meditation_handler))
    application.add_handler(CommandHandler("fitness", fitness_handler))
    application.add_handler(CommandHandler("healer", healer_handler))
    application.add_handler(CommandHandler("journal", journal_handler))
    application.add_handler(CommandHandler("productivity", productivity_handler))
    application.add_handler(CommandHandler("finance", finance_handler))
    application.add_handler(CommandHandler("stats", stats_handler))

    # Callback query handlers
    application.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))
    application.add_handler(CallbackQueryHandler(setup_callback, pattern="^setup_"))
    application.add_handler(CallbackQueryHandler(main_menu_callback, pattern="^menu_"))
    application.add_handler(CallbackQueryHandler(mood_callback, pattern="^mood_"))
    application.add_handler(CallbackQueryHandler(meditation_callback, pattern="^meditation_"))
    application.add_handler(CallbackQueryHandler(meditation_duration_callback, pattern="^duration_"))
    application.add_handler(CallbackQueryHandler(fitness_callback, pattern="^fitness_"))
    application.add_handler(CallbackQueryHandler(journal_callback, pattern="^journal_"))
    application.add_handler(CallbackQueryHandler(finance_callback, pattern="^finance_"))
    application.add_handler(CallbackQueryHandler(stats_callback, pattern="^stats_"))

    # Message handlers for specific contexts
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.Regex(r"^(😊|😢|😠|😰|😴|🤗)"),
        save_mood_handler
    ))

    # Healer mode message handler (when user is in healer mode)
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        healer_message_handler
    ), group=1)

    # Productivity mode message handler
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        productivity_message_handler
    ), group=2)

    # Journal entry handler
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        save_journal_handler
    ), group=3)

    # Workout logging handler
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        log_workout_handler
    ), group=4)

    # Expense logging handler
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        add_expense_handler
    ), group=5)

    logger.info("Bot started successfully. Polling for updates...")

    # Start polling
    application.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise
