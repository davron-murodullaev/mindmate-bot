"""
Reminders handler
"""
import logging

from telegram import Update
from telegram.ext import ContextTypes

from mindmate.services.user_service import user_service
from mindmate.db.queries import (
    create_reminder,
    get_user_reminders,
    count_active_reminders,
    is_premium_active,
)
from mindmate.reminders.parser import (
    parse_reminder,
    format_reminder_time,
    validate_reminder_time,
)
from mindmate.ui.keyboards import (
    get_reminders_keyboard,
    get_back_to_menu_keyboard,
)
from mindmate.i18n import t
from mindmate.core.constants import FREE_MAX_REMINDERS

logger = logging.getLogger(__name__)


async def reminders_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /reminders command — show the reminders sub-menu."""
    user = update.effective_user
    message = update.message
    try:
        lang = await user_service.get_user_language(user.id)
        await message.reply_text(
            t("reminders.welcome", lang),
            reply_markup=get_reminders_keyboard(lang),
        )
    except Exception as e:
        logger.error(f"Error in reminders_handler: {e}")
        await message.reply_text("Reminders")


async def reminders_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle reminder_* callbacks."""
    query = update.callback_query
    user = query.from_user
    try:
        await query.answer()
        lang = await user_service.get_user_language(user.id)
        data = query.data or ""

        if data == "reminder_new":
            # Premium gating: free users limited to FREE_MAX_REMINDERS active
            if not await is_premium_active(user.id):
                count = await count_active_reminders(user.id)
                if count >= FREE_MAX_REMINDERS:
                    await query.edit_message_text(
                        text=t("reminders.limit_reached", lang).format(
                            limit=FREE_MAX_REMINDERS
                        ),
                        reply_markup=get_back_to_menu_keyboard(lang),
                    )
                    return

            context.user_data["waiting_for_reminder"] = True
            await query.edit_message_text(
                text=t("reminders.set", lang),
                reply_markup=get_back_to_menu_keyboard(lang),
            )

        elif data == "reminder_list":
            reminders = await get_user_reminders(user.id, include_sent=False)
            if not reminders:
                text = t("reminders.no_reminders", lang)
            else:
                lines = [
                    t("reminders.list_item", lang).format(
                        time=format_reminder_time(r["reminder_time"]),
                        text=r["text"],
                    )
                    for r in reminders[:20]
                ]
                text = "📋\n" + "\n".join(lines)
            await query.edit_message_text(
                text=text,
                reply_markup=get_back_to_menu_keyboard(lang),
            )

    except Exception as e:
        logger.error(f"Error in reminders_callback: {e}")
        try:
            await query.edit_message_text("Reminders")
        except Exception:
            pass


async def reminder_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the user's free-text reminder input."""
    user = update.effective_user
    message = update.message
    try:
        if not context.user_data.get("waiting_for_reminder"):
            return  # Not for us

        if not message or not message.text:
            return

        lang = await user_service.get_user_language(user.id)

        parsed = parse_reminder(message.text)
        if not parsed or not validate_reminder_time(parsed[1]):
            await message.reply_text(
                t("reminders.parse_error", lang),
                reply_markup=get_back_to_menu_keyboard(lang),
            )
            return

        reminder_text, reminder_time, repeat_type = parsed
        await create_reminder(user.id, reminder_text, reminder_time, repeat_type)
        context.user_data["waiting_for_reminder"] = False

        await message.reply_text(
            t("reminders.created", lang).format(
                text=reminder_text,
                time=format_reminder_time(reminder_time),
            ),
            reply_markup=get_back_to_menu_keyboard(lang),
        )

    except Exception as e:
        logger.error(f"Error in reminder_text_handler: {e}")
        await message.reply_text("Error creating reminder.")
