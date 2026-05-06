"""
Start command handler
"""
import logging

from telegram import Update
from telegram.ext import ContextTypes

from mindmate.services.user_service import user_service
from mindmate.ui.keyboards import (
    get_language_keyboard,
    get_setup_keyboard,
    get_main_menu_keyboard,
)
from mindmate.i18n import t
from mindmate.core.constants import SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE

logger = logging.getLogger(__name__)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user = update.effective_user
    message = update.message

    try:
        # Create or get user
        await user_service.get_or_create_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
        )

        # Get user language (falls back to default if missing)
        lang = await user_service.get_user_language(user.id)

        # Send welcome message with language selection
        await message.reply_text(
            t("welcome", lang),
            reply_markup=get_language_keyboard(),
        )

    except Exception as e:
        logger.error(f"Error in start_handler: {e}")
        await message.reply_text(
            "Welcome to MindMate! Please select your language:",
            reply_markup=get_language_keyboard(),
        )


async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle language selection callback."""
    query = update.callback_query
    user = query.from_user

    try:
        await query.answer()

        # Extract & validate language
        raw_lang = (query.data or "").replace("lang_", "").strip().lower()
        lang = raw_lang if raw_lang in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE

        # Persist
        await user_service.set_user_language(user.id, lang)

        await query.edit_message_text(
            text=t("setup.complete", lang),
            reply_markup=get_setup_keyboard(lang),
        )

    except Exception as e:
        logger.error(f"Error in language_callback: {e}")
        try:
            await query.edit_message_text("Language updated!")
        except Exception:
            pass


async def setup_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle setup completion callback."""
    query = update.callback_query
    user = query.from_user

    try:
        await query.answer()

        lang = await user_service.get_user_language(user.id)

        await query.edit_message_text(
            text=t("menu.main_menu", lang),
            reply_markup=get_main_menu_keyboard(lang),
        )

    except Exception as e:
        logger.error(f"Error in setup_callback: {e}")
        try:
            await query.edit_message_text("Welcome! What would you like to do?")
        except Exception:
            pass
