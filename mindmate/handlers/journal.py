"""
Journal Handler - Handles journal entry creation, viewing, and management
"""

from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, filters
from mindmate.i18n.loader import get_text
from mindmate.ui.keyboards import get_main_menu_keyboard


async def journal_command(update, context):
    """Handle the /journal command"""
    await update.message.reply_text("Handler journal works! Journaling feature coming soon...")


def register_journal_handlers(app):
    """Register all journal-related handlers"""
    app.add_handler(CommandHandler("journal", journal_command))
