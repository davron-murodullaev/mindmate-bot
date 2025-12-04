"""
Meditation Handler - Handles meditation sessions and guided meditation flows
"""

from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, filters
from mindmate.i18n.loader import get_text
from mindmate.ui.keyboards import get_main_menu_keyboard


async def meditation_command(update, context):
    """Handle the /meditation command"""
    await update.message.reply_text("Handler meditation works! Meditation sessions coming soon...")


def register_meditation_handlers(app):
    """Register all meditation-related handlers"""
    app.add_handler(CommandHandler("meditation", meditation_command))
