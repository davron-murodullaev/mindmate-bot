"""
Meditation handler
"""
from telegram import Update
from telegram.ext import ContextTypes
import logging
import asyncio

from mindmate.services.user_service import user_service
from mindmate.db.queries import create_meditation_session
from mindmate.ui.keyboards import get_meditation_keyboard, get_back_to_menu_keyboard
from mindmate.i18n import t

logger = logging.getLogger(__name__)


async def meditation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /meditation command."""
    user = update.effective_user
    message = update.message

    try:
        lang = await user_service.get_user_language(user.id)

        await message.reply_text(
            t("meditation.welcome", lang),
            reply_markup=get_meditation_keyboard(lang)
        )

    except Exception as e:
        logger.error(f"Error in meditation_handler: {e}")
        await message.reply_text("Welcome to Meditation")


async def meditation_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle meditation menu callback."""
    query = update.callback_query
    user = query.from_user

    try:
        await query.answer()

        lang = await user_service.get_user_language(user.id)

        await query.edit_message_text(
            text=t("meditation.welcome", lang),
            reply_markup=get_meditation_keyboard(lang)
        )

    except Exception as e:
        logger.error(f"Error in meditation_callback: {e}")
        await query.edit_message_text("Select meditation duration")


async def meditation_duration_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle meditation duration selection."""
    query = update.callback_query
    user = query.from_user

    try:
        await query.answer()

        lang = await user_service.get_user_language(user.id)

        # Extract duration
        duration = int(query.data.replace("duration_", ""))

        # Start meditation session
        await query.edit_message_text(
            text=t("meditation.start", lang, duration=duration)
        )

        # Wait for duration (simulate)
        # In production, you'd use a proper timer/scheduler

        # Save meditation session
        await create_meditation_session(user.id, duration)

        # Send completion message after a short delay
        await asyncio.sleep(2)
        await query.message.reply_text(
            text=t("meditation.complete", lang, duration=duration),
            reply_markup=get_back_to_menu_keyboard(lang)
        )

    except Exception as e:
        logger.error(f"Error in meditation_duration_callback: {e}")
        await query.edit_message_text("Meditation session started!")
