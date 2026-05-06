"""
Menu handler with proper callback routing for every menu_* button.
"""
import logging

from telegram import Update
from telegram.ext import ContextTypes

from mindmate.services.user_service import user_service
from mindmate.ui.keyboards import (
    get_main_menu_keyboard,
    get_mood_keyboard,
    get_journal_keyboard,
    get_reminders_keyboard,
    get_stats_keyboard,
    get_settings_keyboard,
    get_premium_keyboard,
    get_back_to_menu_keyboard,
)
from mindmate.i18n import t

logger = logging.getLogger(__name__)


async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /menu command."""
    user = update.effective_user
    message = update.message
    try:
        # Reset any active mode when user explicitly opens menu
        context.user_data.pop("mode", None)
        context.user_data.pop("waiting_for_journal", None)
        context.user_data.pop("waiting_for_reminder", None)

        lang = await user_service.get_user_language(user.id)
        await message.reply_text(
            t("menu.main_menu", lang),
            reply_markup=get_main_menu_keyboard(lang),
        )
    except Exception as e:
        logger.error(f"Error in menu_handler: {e}")
        await message.reply_text("Main Menu")


async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Route every menu_* callback to the appropriate sub-screen."""
    query = update.callback_query
    user = query.from_user

    try:
        await query.answer()
        lang = await user_service.get_user_language(user.id)
        data = query.data  # e.g. "menu_main", "menu_mood", ...

        # Always clear any waiting/mode state when navigating menus
        context.user_data.pop("mode", None)
        context.user_data.pop("waiting_for_journal", None)
        context.user_data.pop("waiting_for_reminder", None)

        if data == "menu_main":
            await query.edit_message_text(
                text=t("menu.main_menu", lang),
                reply_markup=get_main_menu_keyboard(lang),
            )

        elif data == "menu_mood":
            await query.edit_message_text(
                text=t("mood.select", lang),
                reply_markup=get_mood_keyboard(lang),
            )

        elif data == "menu_journal":
            await query.edit_message_text(
                text=t("journal.welcome", lang),
                reply_markup=get_journal_keyboard(lang),
            )

        elif data == "menu_reminders":
            await query.edit_message_text(
                text=t("reminders.welcome", lang),
                reply_markup=get_reminders_keyboard(lang),
            )

        elif data == "menu_stats":
            await query.edit_message_text(
                text=t("stats.welcome", lang),
                reply_markup=get_stats_keyboard(lang),
            )

        elif data == "menu_healer":
            context.user_data["mode"] = "healer"
            await query.edit_message_text(
                text=t("healer.welcome", lang),
                reply_markup=get_back_to_menu_keyboard(lang),
            )

        elif data == "menu_productivity":
            context.user_data["mode"] = "productivity"
            await query.edit_message_text(
                text=t("productivity.welcome", lang),
                reply_markup=get_back_to_menu_keyboard(lang),
            )

        elif data == "menu_settings":
            await query.edit_message_text(
                text=t("settings.welcome", lang),
                reply_markup=get_settings_keyboard(lang),
            )

        elif data == "menu_premium":
            await query.edit_message_text(
                text=t("premium.welcome", lang),
                reply_markup=get_premium_keyboard(lang),
            )

        else:
            # Unknown menu_* callback — fall back to main menu
            logger.warning(f"Unknown menu callback: {data}")
            await query.edit_message_text(
                text=t("menu.main_menu", lang),
                reply_markup=get_main_menu_keyboard(lang),
            )

    except Exception as e:
        logger.error(f"Error in main_menu_callback: {e}")
        try:
            await query.edit_message_text("Main Menu")
        except Exception:
            pass
