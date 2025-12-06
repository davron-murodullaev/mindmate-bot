"""
Finance tracking handler
"""
from telegram import Update
from telegram.ext import ContextTypes
import logging
import re

from mindmate.services.user_service import user_service
from mindmate.services.stats_service import stats_service
from mindmate.db.queries import create_expense
from mindmate.ui.keyboards import get_finance_keyboard, get_back_to_menu_keyboard
from mindmate.ui.layouts import format_finance_stats, format_expense_categories
from mindmate.i18n import t

logger = logging.getLogger(__name__)


async def finance_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /finance command."""
    user = update.effective_user
    message = update.message

    try:
        lang = await user_service.get_user_language(user.id)

        await message.reply_text(
            t("finance.welcome", lang),
            reply_markup=get_finance_keyboard(lang)
        )

    except Exception as e:
        logger.error(f"Error in finance_handler: {e}")
        await message.reply_text("Finance Tracking")


async def finance_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle finance callback."""
    query = update.callback_query
    user = query.from_user

    try:
        await query.answer()

        lang = await user_service.get_user_language(user.id)

        if query.data == "finance_add":
            await query.edit_message_text(
                text=t("finance.enter_expense", lang)
            )
            context.user_data['waiting_for_expense'] = True

        elif query.data == "finance_stats":
            stats = await stats_service.get_finance_statistics(user.id, days=30)
            stats_text = format_finance_stats(stats, lang, days=30)

            if stats.get('categories'):
                stats_text += "\n\n" + format_expense_categories(stats['categories'], lang)

            await query.edit_message_text(
                text=stats_text,
                reply_markup=get_back_to_menu_keyboard(lang)
            )

    except Exception as e:
        logger.error(f"Error in finance_callback: {e}")
        await query.edit_message_text("Finance menu")


async def add_expense_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle expense adding from text message."""
    user = update.effective_user
    message = update.message

    try:
        if not context.user_data.get('waiting_for_expense'):
            return

        text = message.text
        lang = await user_service.get_user_language(user.id)

        # Parse expense: "Amount Category: Description"
        match = re.match(r'(\d+\.?\d*)\s+(\w+):\s*(.+)', text)
        if match:
            amount = float(match.group(1))
            category = match.group(2).strip()
            description = match.group(3).strip()

            # Create expense
            await create_expense(user.id, amount, category, description)

            await message.reply_text(
                t("finance.added", lang, amount=f"{amount:.2f}", category=category),
                reply_markup=get_back_to_menu_keyboard(lang)
            )

            context.user_data['waiting_for_expense'] = False
        else:
            await message.reply_text(t("errors.invalid_input", lang))

    except Exception as e:
        logger.error(f"Error in add_expense_handler: {e}")
        await message.reply_text("Error adding expense")
