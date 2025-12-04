"""
Productivity Handler - Handles task management, productivity tips, and time tracking
"""

from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, filters
from mindmate.i18n.loader import get_text
from mindmate.ui.keyboards import get_main_menu_keyboard


async def productivity_command(update, context):
    """Handle the /productivity command"""
    await update.message.reply_text("Handler productivity works! Task management coming soon...")


def register_productivity_handlers(app):
    """Register all productivity-related handlers"""
    app.add_handler(CommandHandler("productivity", productivity_command))
