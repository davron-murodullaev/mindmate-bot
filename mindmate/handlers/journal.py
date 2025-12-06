"""
Journal handler
"""
from telegram import Update
from telegram.ext import ContextTypes
import logging

from mindmate.services.user_service import user_service
from mindmate.services.journal_service import journal_service
from mindmate.ui.keyboards import get_journal_keyboard, get_back_to_menu_keyboard
from mindmate.ui.layouts import format_journal_entry
from mindmate.i18n import t

logger = logging.getLogger(__name__)


async def journal_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /journal command."""
    user = update.effective_user
    message = update.message

    try:
        lang = await user_service.get_user_language(user.id)

        await message.reply_text(
            t("journal.welcome", lang),
            reply_markup=get_journal_keyboard(lang)
        )

    except Exception as e:
        logger.error(f"Error in journal_handler: {e}")
        await message.reply_text("Journal")


async def journal_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle journal callback."""
    query = update.callback_query
    user = query.from_user

    try:
        await query.answer()

        lang = await user_service.get_user_language(user.id)

        if query.data == "journal_new":
            await query.edit_message_text(
                text=t("journal.enter_text", lang)
            )
            context.user_data['waiting_for_journal'] = True

        elif query.data == "journal_view":
            entries = await journal_service.get_entries(user.id, limit=5)
            if entries:
                entry_text = format_journal_entry(entries[0], lang)
                await query.edit_message_text(
                    text=entry_text,
                    reply_markup=get_back_to_menu_keyboard(lang)
                )
            else:
                await query.edit_message_text(
                    text=t("journal.no_entries", lang),
                    reply_markup=get_back_to_menu_keyboard(lang)
                )

    except Exception as e:
        logger.error(f"Error in journal_callback: {e}")
        await query.edit_message_text("Journal menu")


async def save_journal_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle journal entry saving."""
    user = update.effective_user
    message = update.message

    try:
        if not context.user_data.get('waiting_for_journal'):
            return

        text = message.text
        lang = await user_service.get_user_language(user.id)

        # Save journal entry
        await journal_service.create_entry(user.id, text)

        await message.reply_text(
            t("journal.saved", lang),
            reply_markup=get_back_to_menu_keyboard(lang)
        )

        context.user_data['waiting_for_journal'] = False

    except Exception as e:
        logger.error(f"Error in save_journal_handler: {e}")
        await message.reply_text("Error saving journal entry")
