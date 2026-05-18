"""
Menu handler — routing for the main menu.
"""
import logging

from telegram import Update
from telegram.ext import ContextTypes

from mindmate.services.user_service import user_service
from mindmate.ui.keyboards import (
    get_main_menu_keyboard,
    get_profile_menu_keyboard,
    get_settings_keyboard,
    get_premium_keyboard,
    get_back_to_profile_keyboard,
)
from mindmate.i18n import t

logger = logging.getLogger(__name__)


def _clear_state(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear all transient state when navigating menus."""
    for key in (
        "mode",
        "exam_setup",
        "exam_edit",
        "career_setup",
        "career_edit",
        "career_action",
        "interview_question",
        "last_practice_question",
        "friends_setup",
        "friends_pref_age",
    ):
        context.user_data.pop(key, None)


async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /menu command — open main menu."""
    user = update.effective_user
    message = update.message
    try:
        _clear_state(context)
        lang = await user_service.get_user_language(user.id)
        await message.reply_text(
            t("menu.main_menu", lang),
            reply_markup=get_main_menu_keyboard(lang),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Error in menu_handler: {e}")
        await message.reply_text("Main Menu")


async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Route every menu_* callback."""
    query = update.callback_query
    user = query.from_user

    try:
        await query.answer()
        lang = await user_service.get_user_language(user.id)
        data = query.data

        _clear_state(context)

        if data == "menu_main":
            await query.edit_message_text(
                text=t("menu.main_menu", lang),
                reply_markup=get_main_menu_keyboard(lang),
                parse_mode="Markdown",
            )

        elif data == "menu_exam":
            from mindmate.handlers.exam import exam_handler
            try:
                await query.delete_message()
            except Exception:
                pass
            await exam_handler(update, context)

        elif data == "menu_career":
            from mindmate.handlers.career import career_handler
            try:
                await query.delete_message()
            except Exception:
                pass
            await career_handler(update, context)

        elif data == "menu_friends":
            from mindmate.handlers.friends import friends_handler
            try:
                await query.delete_message()
            except Exception:
                pass
            await friends_handler(update, context)

        elif data == "menu_profile":
            from mindmate.handlers.profile import profile_callback
            await profile_callback(update, context)

        elif data == "menu_healer":
            context.user_data["mode"] = "healer"
            await query.edit_message_text(
                text=t("healer.welcome", lang),
                reply_markup=get_back_to_profile_keyboard(lang),
            )

        elif data == "menu_productivity":
            context.user_data["mode"] = "productivity"
            await query.edit_message_text(
                text=t("productivity.welcome", lang),
                reply_markup=get_back_to_profile_keyboard(lang),
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
            logger.warning(f"Unknown menu callback: {data}")
            await query.edit_message_text(
                text=t("menu.main_menu", lang),
                reply_markup=get_main_menu_keyboard(lang),
                parse_mode="Markdown",
            )

    except Exception as e:
        logger.error(f"Error in main_menu_callback: {e}")
        try:
            await query.edit_message_text("Main Menu")
        except Exception:
            pass
