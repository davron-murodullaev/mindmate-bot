"""
Finance Handler - Handles expense tracking, budget management, and financial insights
"""

from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, filters
from mindmate.i18n.loader import get_text
from mindmate.ui.keyboards import get_main_menu_keyboard


async def finance_command(update, context):
    """Handle the /finance command"""
    await update.message.reply_text("Handler finance works! Expense tracking coming soon...")


def register_finance_handlers(app):
    """Register all finance-related handlers"""
    app.add_handler(CommandHandler("finance", finance_command))
