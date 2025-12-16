"""
Productivity mode handler
"""
from telegram import Update
from telegram.ext import ContextTypes
import logging

from mindmate.services.user_service import user_service
from mindmate.ai_orchestrator import ai_orchestrator
from mindmate.ui.keyboards import get_back_to_menu_keyboard
from mindmate.i18n import t

logger = logging.getLogger(__name__)


async def productivity_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /productivity command."""
    user = update.effective_user
    message = update.message

    try:
        lang = await user_service.get_user_language(user.id)

        await message.reply_text(
            t("productivity.welcome", lang),
            reply_markup=get_back_to_menu_keyboard(lang)
        )

        # Set user state to productivity mode
        context.user_data['mode'] = 'productivity'

    except Exception as e:
        logger.error(f"Error in productivity_handler: {e}")
        await message.reply_text("Welcome to Productivity Coach")


async def productivity_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle messages in productivity mode."""
    user = update.effective_user
    message = update.message

    try:
        # Only process if in productivity mode
        if context.user_data.get('mode') != 'productivity':
            return

        lang = await user_service.get_user_language(user.id)

        # Process message through productivity AI
        response = await ai_orchestrator.process_message(
            user_id=user.id,
            message=message.text,
            mode="productivity"
        )

        await message.reply_text(response)

    except Exception as e:
        logger.error(f"Error in productivity_message_handler: {e}")
        await message.reply_text("Let's work on your productivity goals!")
