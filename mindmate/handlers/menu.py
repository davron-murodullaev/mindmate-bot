"""
Menu handler
"""
from telegram import Update
from telegram.ext import ContextTypes
import logging

from mindmate.services.user_service import user_service
from mindmate.ui.keyboards import get_main_menu_keyboard
from mindmate.i18n import t

logger = logging.getLogger(__name__)


async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /menu command."""
    user = update.effective_user
    message = update.message

    try:
        lang = await user_service.get_user_language(user.id)

        await message.reply_text(
            t("menu.main_menu", lang),
            reply_markup=get_main_menu_keyboard(lang)
        )

    except Exception as e:
        logger.error(f"Error in menu_handler: {e}")
        await message.reply_text("Main Menu")


async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle main menu callback."""
    query = update.callback_query
    user = query.from_user

    try:
        await query.answer()

        lang = await user_service.get_user_language(user.id)

        # Show main menu
        await query.edit_message_text(
            text=t("menu.main_menu", lang),
            reply_markup=get_main_menu_keyboard(lang)
        )

    except Exception as e:
        logger.error(f"Error in main_menu_callback: {e}")
        await query.edit_message_text("Main Menu")
