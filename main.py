"""
MindMate Bot - Main Entry Point

Conversational-first design: every text and voice message is routed
through the AI router first (which can call tools like create_reminder).
Wizards (exam/career/friends setup) take priority when active.
"""
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    PreCheckoutQueryHandler,
    filters,
)

from mindmate.core.config import settings
from mindmate.core.logger import setup_logger
from mindmate.db.connection import init_db, close_pool
from mindmate.reminders.scheduler import start_scheduler, stop_scheduler
from mindmate.api.aiohttp_server import start_web_server, stop_web_server

# Handlers
from mindmate.handlers.start import (
    start_handler,
    language_callback,
    setup_callback,
    cancel_handler,
)
from mindmate.handlers.menu import menu_handler, main_menu_callback
from mindmate.handlers.healer import healer_handler, healer_message_handler
from mindmate.handlers.productivity import productivity_handler, productivity_message_handler
from mindmate.handlers.settings import settings_handler, settings_callback
from mindmate.handlers.premium import premium_handler, premium_callback
from mindmate.handlers.exam import exam_handler, exam_callback, exam_text_handler
from mindmate.handlers.career import career_handler, career_callback, career_text_handler
from mindmate.handlers.profile import profile_handler, profile_callback, profile_action_callback
from mindmate.handlers.friends import (
    friends_handler,
    friends_callback,
    friends_text_handler,
    friends_photo_handler,
)
from mindmate.handlers.legal import privacy_handler, terms_handler, legal_callback
from mindmate.handlers.admin import stats_admin_handler
from mindmate.handlers.payments import (
    buy_premium_handler,
    buy_callback,
    precheckout_handler,
    successful_payment_handler,
)

# AI router
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

_CACHE_LANG_KEY = "_cached_lang"


def _should_serve_http() -> bool:
    """True when a cloud platform has injected $PORT — need HTTP for health checks."""
    import os
    return bool(os.environ.get("PORT") or os.environ.get("RAILWAY_ENVIRONMENT"))


async def _get_lang(user_id: int, context) -> str:
    """Return user language, using context.user_data as a session cache."""
    if _CACHE_LANG_KEY not in context.user_data:
        context.user_data[_CACHE_LANG_KEY] = await user_service.get_user_language(user_id)
    return context.user_data[_CACHE_LANG_KEY]


async def post_init(application: Application) -> None:
    try:
        await init_db()
        logger.info("Database initialized successfully")
        await start_scheduler(application.bot)
        logger.info("Reminder scheduler started")
        # Start HTTP server when Mini App is enabled OR when $PORT is injected
        # by the platform (Railway/Render) so health checks always pass.
        if settings.ENABLE_WEBAPP or _should_serve_http():
            await start_web_server()
    except Exception as e:
        logger.error(f"Error during post-init: {e}")
        raise


async def post_stop(application: Application) -> None:
    try:
        await stop_scheduler()
        logger.info("Reminder scheduler stopped")
        if settings.ENABLE_WEBAPP or _should_serve_http():
            await stop_web_server()
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
    lang = await _get_lang(user.id, context)

    # Free-tier daily limit
    if not await is_premium_active(user.id):
        usage = await get_daily_usage(user.id)
        if usage["ai_messages"] >= FREE_DAILY_AI_MESSAGES:
            await chat.send_message(
                t("premium.limit_reached", lang).format(limit=FREE_DAILY_AI_MESSAGES),
            )
            return

    try:
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

        if open_menu:
            await _open_menu_for_user(update, context, open_menu)

        await increment_ai_usage(user.id)

    except Exception as e:
        logger.error(f"AI router error: {e}")
        await chat.send_message(t("errors.generic", lang))


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
        elif menu == "healer":
            context.user_data["mode"] = "healer"
        elif menu == "productivity":
            context.user_data["mode"] = "productivity"
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

    # Active wizards (highest priority — they need exact input)
    if context.user_data.get("exam_setup") or context.user_data.get("exam_edit") or context.user_data.get("mode") == "exam":
        await exam_text_handler(update, context)
        return

    if context.user_data.get("career_setup") or context.user_data.get("career_edit") or context.user_data.get("mode") == "career":
        await career_text_handler(update, context)
        return

    if context.user_data.get("friends_setup") or context.user_data.get("friends_pref_age"):
        await friends_text_handler(update, context)
        return

    # Specific AI modes (healer/productivity)
    mode = context.user_data.get("mode")
    if mode == "healer":
        await healer_message_handler(update, context)
        return
    if mode == "productivity":
        await productivity_message_handler(update, context)
        return

    # DEFAULT: Route through AI router
    await _route_via_ai(update, context, text)


async def voice_dispatcher(update, context):
    """Handle voice messages — transcribe and route through AI."""
    if not update.message or not update.message.voice:
        return

    user = update.effective_user
    chat = update.effective_chat

    try:
        await chat.send_action("typing")

        lang = await _get_lang(user.id, context)
        language_hint = lang if lang in ("uz", "ru", "en") else None

        voice = update.message.voice
        # Reject files larger than 25 MB (Whisper API limit)
        if voice.file_size and voice.file_size > 25 * 1024 * 1024:
            await chat.send_message(t("voice.too_large", lang))
            return
        voice_file = await voice.get_file()
        audio_bytes = await voice_file.download_as_bytearray()

        text = await transcribe_voice(
            bytes(audio_bytes),
            filename="voice.ogg",
            language_hint=language_hint,
        )
        if not text:
            await chat.send_message(t("voice.not_understood", lang))
            return

        await chat.send_message(t("voice.heard", lang).format(text=text), parse_mode="Markdown")
        await _route_via_ai(update, context, text)

    except Exception as e:
        logger.error(f"Voice dispatcher error: {e}")
        _err_lang = context.user_data.get(_CACHE_LANG_KEY, "en")
        await chat.send_message(t("voice.error", _err_lang))


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
    application.add_handler(CommandHandler("healer", healer_handler))
    application.add_handler(CommandHandler("productivity", productivity_handler))
    application.add_handler(CommandHandler("settings", settings_handler))
    application.add_handler(CommandHandler("premium", premium_handler))
    application.add_handler(CommandHandler("exam", exam_handler))
    application.add_handler(CommandHandler("career", career_handler))
    application.add_handler(CommandHandler("profile", profile_handler))
    application.add_handler(CommandHandler("friends", friends_handler))
    application.add_handler(CommandHandler("cancel", cancel_handler))
    application.add_handler(CommandHandler("privacy", privacy_handler))
    application.add_handler(CommandHandler("terms", terms_handler))
    application.add_handler(CommandHandler("stats_admin", stats_admin_handler))
    application.add_handler(CommandHandler("buy_premium", buy_premium_handler))

    # ── Callback queries ──────────────────────────────────────────────
    application.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))
    application.add_handler(CallbackQueryHandler(setup_callback, pattern="^setup_"))
    application.add_handler(CallbackQueryHandler(main_menu_callback, pattern="^menu_"))
    application.add_handler(CallbackQueryHandler(settings_callback, pattern="^settings_"))
    application.add_handler(CallbackQueryHandler(premium_callback, pattern="^premium_"))
    application.add_handler(CallbackQueryHandler(exam_callback, pattern="^exam_"))
    application.add_handler(CallbackQueryHandler(career_callback, pattern="^career_"))
    application.add_handler(CallbackQueryHandler(profile_action_callback, pattern="^profile_"))
    application.add_handler(CallbackQueryHandler(friends_callback, pattern="^friends_"))
    application.add_handler(CallbackQueryHandler(legal_callback, pattern="^legal_"))
    application.add_handler(CallbackQueryHandler(buy_callback, pattern="^buy_"))

    # ── Telegram Stars payments ───────────────────────────────────────
    application.add_handler(PreCheckoutQueryHandler(precheckout_handler))
    application.add_handler(MessageHandler(
        filters.SUCCESSFUL_PAYMENT,
        successful_payment_handler,
    ))

    # ── Text + voice + photo dispatcher ──────────────────────────────
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_dispatcher))
    application.add_handler(MessageHandler(filters.VOICE, voice_dispatcher))
    application.add_handler(MessageHandler(
        filters.PHOTO | filters.Document.IMAGE,
        friends_photo_handler,
    ))

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
