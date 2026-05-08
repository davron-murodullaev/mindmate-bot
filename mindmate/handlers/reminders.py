"""
Reminders handler with delete buttons + free-tier gating.
"""
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from mindmate.services.user_service import user_service
from mindmate.db.queries import (
    create_reminder,
    get_user_reminders,
    count_active_reminders,
    delete_reminder,
    is_premium_active,
)
from mindmate.db.connection import execute_query
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


def _build_list_keyboard(reminders: list, lang: str) -> InlineKeyboardMarkup:
    """Build a keyboard listing reminders with a per-item delete button."""
    rows = []
    for r in reminders[:10]:  # Show up to 10 with buttons
        time_str = format_reminder_time(r["reminder_time"])
        # Truncate long reminder text for button label
        label = r["text"][:30] + ("…" if len(r["text"]) > 30 else "")
        rows.append([InlineKeyboardButton(
            f"🗑 {time_str} — {label}",
            callback_data=f"reminder_del_{r['id']}",
        )])
    rows.append([InlineKeyboardButton(t("buttons.back", lang), callback_data="menu_reminders")])
    return InlineKeyboardMarkup(rows)


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

        if data == "menu_reminders":
            # Returned via Back button — re-render menu
            await query.edit_message_text(
                text=t("reminders.welcome", lang),
                reply_markup=get_reminders_keyboard(lang),
            )
            return

        if data == "reminder_new":
            # Free-tier limit
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
            return

        if data == "reminder_list":
            reminders = await get_user_reminders(user.id, include_sent=False)
            if not reminders:
                await query.edit_message_text(
                    text=t("reminders.no_reminders", lang),
                    reply_markup=get_back_to_menu_keyboard(lang),
                )
                return

            text = t("reminders.list_header", lang) + "\n\n"
            text += "\n".join(
                t("reminders.list_item", lang).format(
                    time=format_reminder_time(r["reminder_time"]),
                    text=r["text"],
                )
                for r in reminders[:10]
            )
            text += "\n\n" + t("reminders.tap_to_delete", lang)

            await query.edit_message_text(
                text=text,
                reply_markup=_build_list_keyboard(reminders, lang),
            )
            return

        if data.startswith("reminder_del_"):
            reminder_id_str = data.replace("reminder_del_", "")
            try:
                reminder_id = int(reminder_id_str)
            except ValueError:
                return
            await delete_reminder(reminder_id, user.id)
            await query.answer(t("reminders.deleted", lang), show_alert=False)
            # Re-show updated list
            reminders = await get_user_reminders(user.id, include_sent=False)
            if not reminders:
                await query.edit_message_text(
                    text=t("reminders.no_reminders", lang),
                    reply_markup=get_back_to_menu_keyboard(lang),
                )
            else:
                text = t("reminders.list_header", lang) + "\n\n"
                text += "\n".join(
                    t("reminders.list_item", lang).format(
                        time=format_reminder_time(r["reminder_time"]),
                        text=r["text"],
                    )
                    for r in reminders[:10]
                )
                text += "\n\n" + t("reminders.tap_to_delete", lang)
                await query.edit_message_text(
                    text=text,
                    reply_markup=_build_list_keyboard(reminders, lang),
                )
            return

        if data == "reminder_delete_all":
            # Confirm step
            await query.edit_message_text(
                text=t("reminders.delete_all_confirm", lang),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(t("buttons.confirm", lang), callback_data="reminder_delete_all_yes")],
                    [InlineKeyboardButton(t("buttons.cancel", lang), callback_data="menu_reminders")],
                ]),
            )
            return

        if data == "reminder_delete_all_yes":
            await execute_query(
                "DELETE FROM reminders WHERE user_id = $1 AND is_sent = false",
                user.id,
            )
            await query.edit_message_text(
                text=t("reminders.all_deleted", lang),
                reply_markup=get_back_to_menu_keyboard(lang),
            )
            return

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
            return

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
