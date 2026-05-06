"""
Productivity mode handler
"""
import logging

from telegram import Update
from telegram.ext import ContextTypes

from mindmate.services.user_service import user_service
from mindmate.db.queries import (
    increment_ai_usage,
    get_daily_usage,
    is_premium_active,
)
from mindmate.ai.memory import ConversationMemory
from mindmate.ai.engines.productivity_engine import ProductivityEngine
from mindmate.ai.formatter import format_response
from mindmate.ui.keyboards import get_back_to_menu_keyboard
from mindmate.i18n import t
from mindmate.core.constants import FREE_DAILY_AI_MESSAGES

logger = logging.getLogger(__name__)

_memory = ConversationMemory()
_engine = ProductivityEngine()


async def productivity_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /productivity command."""
    user = update.effective_user
    message = update.message
    try:
        lang = await user_service.get_user_language(user.id)
        await message.reply_text(
            t("productivity.welcome", lang),
            reply_markup=get_back_to_menu_keyboard(lang),
        )
        context.user_data["mode"] = "productivity"
    except Exception as e:
        logger.error(f"Error in productivity_handler: {e}")
        await message.reply_text("Welcome to Productivity Coach")


async def productivity_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle messages in productivity mode."""
    user = update.effective_user
    message = update.message
    try:
        if context.user_data.get("mode") != "productivity":
            return

        if not message or not message.text:
            return

        lang = await user_service.get_user_language(user.id)

        # Free-tier daily limit
        if not await is_premium_active(user.id):
            usage = await get_daily_usage(user.id)
            if usage["ai_messages"] >= FREE_DAILY_AI_MESSAGES:
                await message.reply_text(
                    t("premium.limit_reached", lang).format(limit=FREE_DAILY_AI_MESSAGES),
                    reply_markup=get_back_to_menu_keyboard(lang),
                )
                return

        history = await _memory.get_history(user.id, "productivity")
        await _memory.add_message(user.id, "productivity", "user", message.text)

        response = await _engine.process(
            message=message.text,
            history=history,
            context={"lang": lang},
        )

        await _memory.add_message(user.id, "productivity", "assistant", response)
        await increment_ai_usage(user.id)

        await message.reply_text(format_response(response, mode="productivity"))

    except Exception as e:
        logger.error(f"Error in productivity_message_handler: {e}")
        await message.reply_text("Let's work on your productivity goals!")
