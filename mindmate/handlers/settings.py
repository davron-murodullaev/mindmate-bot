"""
Settings handler
"""
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from mindmate.services.user_service import user_service
from mindmate.db.queries import delete_user_data
from mindmate.ui.keyboards import (
    get_settings_keyboard,
    get_language_keyboard,
    get_back_to_menu_keyboard,
)
from mindmate.i18n import t

logger = logging.getLogger(__name__)


async def settings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /settings command."""
    user = update.effective_user
    message = update.message
    try:
        lang = await user_service.get_user_language(user.id)
        await message.reply_text(
            t("settings.welcome", lang),
            reply_markup=get_settings_keyboard(lang),
        )
    except Exception as e:
        logger.error(f"Error in settings_handler: {e}")
        await message.reply_text("Settings")


async def settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle settings_* callbacks."""
    query = update.callback_query
    user = query.from_user
    try:
        await query.answer()
        lang = await user_service.get_user_language(user.id)
        data = query.data or ""

        if data == "settings_language":
            await query.edit_message_text(
                text=t("welcome", lang),
                reply_markup=get_language_keyboard(),
            )

        elif data == "settings_timezone":
            await query.edit_message_text(
                text=t("setup.choose_timezone", lang),
                reply_markup=get_back_to_menu_keyboard(lang),
            )

        elif data == "settings_delete":
            confirm_kb = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            t("buttons.confirm", lang),
                            callback_data="settings_delete_confirm",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            t("buttons.cancel", lang),
                            callback_data="menu_settings",
                        )
                    ],
                ]
            )
            await query.edit_message_text(
                text=t("settings.delete_confirm", lang),
                reply_markup=confirm_kb,
            )

        elif data == "settings_delete_confirm":
            await delete_user_data(user.id)
            await query.edit_message_text(
                text=t("settings.delete_done", lang),
            )

    except Exception as e:
        logger.error(f"Error in settings_callback: {e}")
        try:
            await query.edit_message_text("Settings")
        except Exception:
            pass
