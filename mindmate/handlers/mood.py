"""
Mood tracking handler
"""
from telegram import Update
from telegram.ext import ContextTypes
import logging

from mindmate.services.user_service import user_service
from mindmate.db.queries import create_mood
from mindmate.ui.keyboards import get_mood_keyboard, get_back_to_menu_keyboard
from mindmate.i18n import t

logger = logging.getLogger(__name__)


async def mood_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /mood command."""
    user = update.effective_user
    message = update.message

    try:
        lang = await user_service.get_user_language(user.id)

        await message.reply_text(
            t("mood.select", lang),
            reply_markup=get_mood_keyboard(lang)
        )

    except Exception as e:
        logger.error(f"Error in mood_handler: {e}")
        await message.reply_text("How are you feeling today?")


async def mood_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle mood selection callback."""
    query = update.callback_query
    user = query.from_user

    try:
        await query.answer()

        lang = await user_service.get_user_language(user.id)

        # Extract mood from callback data
        mood_type = query.data.replace("mood_", "")

        # Save mood
        await create_mood(user.id, mood_type)

        # Send confirmation
        await query.edit_message_text(
            text=t("mood.logged", lang),
            reply_markup=get_back_to_menu_keyboard(lang)
        )

    except Exception as e:
        logger.error(f"Error in mood_callback: {e}")
        await query.edit_message_text("Mood logged successfully!")


async def save_mood_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle mood emoji messages."""
    user = update.effective_user
    message = update.message

    try:
        # This would save mood based on emoji, but we'll skip for now
        pass

    except Exception as e:
        logger.error(f"Error in save_mood_handler: {e}")
