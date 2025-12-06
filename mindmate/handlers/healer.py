"""
Healer mode handler
"""
from telegram import Update
from telegram.ext import ContextTypes
import logging

from mindmate.services.user_service import user_service
from mindmate.services.healer_service import healer_service
from mindmate.ui.keyboards import get_back_to_menu_keyboard
from mindmate.i18n import t

logger = logging.getLogger(__name__)


async def healer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /healer command."""
    user = update.effective_user
    message = update.message

    try:
        lang = await user_service.get_user_language(user.id)

        await message.reply_text(
            t("healer.welcome", lang),
            reply_markup=get_back_to_menu_keyboard(lang)
        )

        # Set user state to healer mode
        context.user_data['mode'] = 'healer'

    except Exception as e:
        logger.error(f"Error in healer_handler: {e}")
        await message.reply_text("Welcome to Healer mode")


async def healer_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle messages in healer mode."""
    user = update.effective_user
    message = update.message

    try:
        # Only process if in healer mode
        if context.user_data.get('mode') != 'healer':
            return

        lang = await user_service.get_user_language(user.id)

        # Process message through healer AI
        response = await healer_service.process_message(user.id, message.text)

        await message.reply_text(response)

    except Exception as e:
        logger.error(f"Error in healer_message_handler: {e}")
        await message.reply_text("I'm here to listen and support you.")
