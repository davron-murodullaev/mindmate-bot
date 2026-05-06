"""
MindMate Bot - Main Entry Point
"""
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from mindmate.core.config import settings
from mindmate.core.logger import setup_logger
from mindmate.db.connection import init_db, close_pool
from mindmate.reminders.scheduler import start_scheduler, stop_scheduler

# Handlers (simplified set — fitness/finance/meditation removed)
from mindmate.handlers.start import start_handler, language_callback, setup_callback
from mindmate.handlers.menu import menu_handler, main_menu_callback
from mindmate.handlers.mood import mood_handler, mood_callback, save_mood_handler
from mindmate.handlers.healer import healer_handler, healer_message_handler
from mindmate.handlers.journal import journal_handler, journal_callback, save_journal_handler
from mindmate.handlers.productivity import productivity_handler, productivity_message_handler
from mindmate.handlers.stats import stats_handler, stats_callback
from mindmate.handlers.reminders import (
    reminders_handler,
    reminders_callback,
    reminder_text_handler,
)
from mindmate.handlers.settings import settings_handler, settings_callback
from mindmate.handlers.premium import premium_handler, premium_callback

logger = setup_logger(__name__)


async def post_init(application: Application) -> None:
    """Initialize components after application startup."""
    try:
        await init_db()
        logger.info("Database initialized successfully")

        await start_scheduler(application.bot)
        logger.info("Reminder scheduler started")
    except Exception as e:
        logger.error(f"Error during post-init: {e}")
        raise


async def post_stop(application: Application) -> None:
    """Clean up components on application shutdown."""
    try:
        await stop_scheduler()
        logger.info("Reminder scheduler stopped")

        await close_pool()
        logger.info("Database pool closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# ──────────────────────────────────────────────────────────────────────
# Single dispatcher MessageHandler — replaces the 5 conflicting groups.
# Order: mood emoji → reminder text → journal text → healer mode → productivity mode
# ──────────────────────────────────────────────────────────────────────

async def text_dispatcher(update, context):
    """Dispatch a free-text message to the right handler based on user_data state."""
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()

    # 1) Quick mood log via leading emoji (😊 😢 😠 😰 😴 🤗)
    first = text[:1]
    if first in {"😊", "😢", "😠", "😰", "😴", "🤗"}:
        await save_mood_handler(update, context)
        return

    # 2) Pending reminder text
    if context.user_data.get("waiting_for_reminder"):
        await reminder_text_handler(update, context)
        return

    # 3) Pending journal entry
    if context.user_data.get("waiting_for_journal"):
        await save_journal_handler(update, context)
        return

    # 4) Active AI mode
    mode = context.user_data.get("mode")
    if mode == "healer":
        await healer_message_handler(update, context)
        return
    if mode == "productivity":
        await productivity_message_handler(update, context)
        return

    # 5) Otherwise — gentle nudge to use the menu
    try:
        from mindmate.services.user_service import user_service
        from mindmate.ui.keyboards import get_main_menu_keyboard
        from mindmate.i18n import t

        lang = await user_service.get_user_language(update.effective_user.id)
        await update.message.reply_text(
            t("menu.main_menu", lang),
            reply_markup=get_main_menu_keyboard(lang),
        )
    except Exception as e:
        logger.error(f"Error in text_dispatcher fallback: {e}")


def main():
    """Main function to run the bot."""
    logger.info("Starting MindMate Bot...")

    application = (
        Application.builder()
        .token(settings.TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .post_stop(post_stop)
        .build()
    )

    # ── Command handlers ──────────────────────────────────────────────
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("menu", menu_handler))
    application.add_handler(CommandHandler("mood", mood_handler))
    application.add_handler(CommandHandler("healer", healer_handler))
    application.add_handler(CommandHandler("journal", journal_handler))
    application.add_handler(CommandHandler("productivity", productivity_handler))
    application.add_handler(CommandHandler("reminders", reminders_handler))
    application.add_handler(CommandHandler("stats", stats_handler))
    application.add_handler(CommandHandler("settings", settings_handler))
    application.add_handler(CommandHandler("premium", premium_handler))

    # ── Callback query handlers ───────────────────────────────────────
    application.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))
    application.add_handler(CallbackQueryHandler(setup_callback, pattern="^setup_"))
    application.add_handler(CallbackQueryHandler(main_menu_callback, pattern="^menu_"))
    application.add_handler(CallbackQueryHandler(mood_callback, pattern="^mood_"))
    application.add_handler(CallbackQueryHandler(journal_callback, pattern="^journal_"))
    application.add_handler(CallbackQueryHandler(reminders_callback, pattern="^reminder_"))
    application.add_handler(CallbackQueryHandler(stats_callback, pattern="^stats_"))
    application.add_handler(CallbackQueryHandler(settings_callback, pattern="^settings_"))
    application.add_handler(CallbackQueryHandler(premium_callback, pattern="^premium_"))

    # ── Single text dispatcher (replaces 5 conflicting groups) ────────
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, text_dispatcher)
    )

    logger.info("Bot started successfully. Polling for updates...")
    application.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise
