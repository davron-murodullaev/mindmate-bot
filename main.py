"""
MindMate Bot - Main Entry Point

Conversational-first design: every text and voice message is routed
through the AI router first (which can call tools like create_reminder).
Wizards (exam/career setup, journal entry) take priority when active.
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

# Handlers
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
from mindmate.handlers.exam import exam_handler, exam_callback, exam_text_handler
from mindmate.handlers.career import career_handler, career_callback, career_text_handler
from mindmate.handlers.profile import profile_handler, profile_callback
from mindmate.handlers.friends import (
    friends_handler,
    friends_callback,
    friends_text_handler,
    friends_photo_handler,
)

# AI router (the conversational brain)
from mindmate.ai.router import route_message
from mindmate.ai.memory import ConversationMemory
from mindmate.ai.transcription import transcribe_voice
from mindmate.services.user_service import user_service
from mindmate.db.queries import (
    increment_ai_usage,
    get_daily_usage,
    is_premium_active,
)
from mindmate.core.constants import FREE_DAILY_AI_MESSAGES
from mindmate.i18n import t

logger = setup_logger(__name__)
_router_memory = ConversationMemory()


async def post_init(application: Application) -> None:
    try:
        await init_db()
        logger.info("Database initialized successfully")
        await start_scheduler(application.bot)
        logger.info("Reminder scheduler started")
    except Exception as e:
        logger.error(f"Error during post-init: {e}")
        raise


async def post_stop(application: Application) -> None:
    try:
        await stop_scheduler()
        logger.info("Reminder scheduler stopped")
        await close_pool()
        logger.info("Database pool closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# ──────────────────────────────────────────────────────────────────────
# Conversational AI dispatcher
# ──────────────────────────────────────────────────────────────────────

async def _route_via_ai(update, context, user_text: str) -> None:
    """Send a free-text message through the AI router and handle the response."""
    user = update.effective_user
    chat = update.effective_chat
    lang = await user_service.get_user_language(user.id)

    # Free-tier daily limit
    if not await is_premium_active(user.id):
        usage = await get_daily_usage(user.id)
        if usage["ai_messages"] >= FREE_DAILY_AI_MESSAGES:
            await chat.send_message(
                t("premium.limit_reached", lang).format(limit=FREE_DAILY_AI_MESSAGES),
            )
            return

    try:
        # Show "typing..." indicator while AI thinks
        await chat.send_action("typing")

        history = await _router_memory.get_history(user.id, "router")
        await _router_memory.add_message(user.id, "router", "user", user_text)

        result = await route_message(
            user_id=user.id,
            message=user_text,
            history=history,
            lang=lang,
            user_first_name=user.first_name,
        )

        msg_text = result.get("message", "")
        open_menu = result.get("open_menu")

        if msg_text:
            await _router_memory.add_message(user.id, "router", "assistant", msg_text)
            await chat.send_message(msg_text, parse_mode="Markdown")

        # If AI wants to open a menu, fire the corresponding callback
        if open_menu:
            await _open_menu_for_user(update, context, open_menu)

        await increment_ai_usage(user.id)

    except Exception as e:
        logger.error(f"AI router error: {e}")
        await chat.send_message("Texnik xatolik. Qayta urinib ko'ring.")


async def _open_menu_for_user(update, context, menu: str) -> None:
    """Open a specific menu when the AI signals via the open_menu tool."""
    try:
        if menu == "exam":
            await exam_handler(update, context)
        elif menu == "career":
            await career_handler(update, context)
        elif menu == "friends":
            await friends_handler(update, context)
        elif menu == "profile":
            await profile_handler(update, context)
        elif menu == "mood":
            await mood_handler(update, context)
        elif menu == "journal":
            await journal_handler(update, context)
        elif menu == "reminders":
            await reminders_handler(update, context)
        elif menu == "stats":
            await stats_handler(update, context)
        elif menu == "healer":
            await healer_handler(update, context)
        elif menu == "productivity":
            await productivity_handler(update, context)
        elif menu == "settings":
            await settings_handler(update, context)
        elif menu == "premium":
            await premium_handler(update, context)
        else:
            await menu_handler(update, context)
    except Exception as e:
        logger.error(f"Error opening menu '{menu}': {e}")


async def text_dispatcher(update, context):
    """Dispatch a text message to the right handler."""
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()

    # 1) Mood emoji shortcut
    if text[:1] in {"😊", "😢", "😠", "😰", "😴", "🤗"}:
        await save_mood_handler(update, context)
        return

    # 2) Active wizards (highest priority — they need exact input)
    if context.user_data.get("exam_setup") or context.user_data.get("mode") == "exam":
        await exam_text_handler(update, context)
        return

    if context.user_data.get("career_setup") or context.user_data.get("mode") == "career":
        await career_text_handler(update, context)
        return

    if context.user_data.get("friends_setup") or context.user_data.get("friends_pref_age"):
        await friends_text_handler(update, context)
        return

    if context.user_data.get("waiting_for_reminder"):
        await reminder_text_handler(update, context)
        return

    if context.user_data.get("waiting_for_journal"):
        await save_journal_handler(update, context)
        return

    # 3) Specific AI modes (healer/productivity)
    mode = context.user_data.get("mode")
    if mode == "healer":
        await healer_message_handler(update, context)
        return
    if mode == "productivity":
        await productivity_message_handler(update, context)
        return

    # 4) DEFAULT: Route through AI brain (conversational entry)
    await _route_via_ai(update, context, text)


async def voice_dispatcher(update, context):
    """Handle voice messages — transcribe and route through AI."""
    if not update.message or not update.message.voice:
        return

    user = update.effective_user
    chat = update.effective_chat

    try:
        await chat.send_action("typing")

        # Use the user's selected language as a transcription hint.
        # Better accuracy than auto-detect for short voice messages.
        lang = await user_service.get_user_language(user.id)
        # Whisper supports "uz" but understands UZ better when hinted "uz".
        language_hint = lang if lang in ("uz", "ru", "en") else None

        voice = update.message.voice
        voice_file = await voice.get_file()
        audio_bytes = await voice_file.download_as_bytearray()

        text = await transcribe_voice(
            bytes(audio_bytes),
            filename="voice.ogg",
            language_hint=language_hint,
        )
        if not text:
            await chat.send_message(
                "🎙 Ovozli xabarni tushunolmadim. Iltimos, sekinroq va aniqroq "
                "qayta ayting yoki matn ko'rinishida yozib yuboring."
            )
            return

        # Show user what we heard so they can verify/correct
        await chat.send_message(f"🎙 _Eshitganim:_ {text}", parse_mode="Markdown")

        # Now route as if it were a text message
        await _route_via_ai(update, context, text)

    except Exception as e:
        logger.error(f"Voice dispatcher error: {e}")
        await chat.send_message("🎙 Ovozni o'qishda xatolik. Matn ko'rinishida yozib yuboring.")


def main():
    logger.info("Starting MindMate Bot...")

    application = (
        Application.builder()
        .token(settings.TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .post_stop(post_stop)
        .build()
    )

    # ── Commands ──────────────────────────────────────────────────────
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
    application.add_handler(CommandHandler("exam", exam_handler))
    application.add_handler(CommandHandler("career", career_handler))
    application.add_handler(CommandHandler("profile", profile_handler))
    application.add_handler(CommandHandler("friends", friends_handler))

    # ── Callback queries ──────────────────────────────────────────────
    application.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))
    application.add_handler(CallbackQueryHandler(setup_callback, pattern="^setup_"))
    application.add_handler(CallbackQueryHandler(main_menu_callback, pattern="^menu_"))
    application.add_handler(CallbackQueryHandler(mood_callback, pattern="^mood_"))
    application.add_handler(CallbackQueryHandler(journal_callback, pattern="^journal_"))
    application.add_handler(CallbackQueryHandler(reminders_callback, pattern="^reminder_"))
    application.add_handler(CallbackQueryHandler(stats_callback, pattern="^stats_"))
    application.add_handler(CallbackQueryHandler(settings_callback, pattern="^settings_"))
    application.add_handler(CallbackQueryHandler(premium_callback, pattern="^premium_"))
    application.add_handler(CallbackQueryHandler(exam_callback, pattern="^exam_"))
    application.add_handler(CallbackQueryHandler(career_callback, pattern="^career_"))
    application.add_handler(CallbackQueryHandler(friends_callback, pattern="^friends_"))

    # ── Text + voice + photo dispatcher ───────────────────────────────
    # Photo handler covers BOTH wizard photos AND verification selfies
    # (the handler decides what to do based on user_data state).
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_dispatcher))
    application.add_handler(MessageHandler(filters.VOICE, voice_dispatcher))
    application.add_handler(MessageHandler(filters.PHOTO, friends_photo_handler))

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
