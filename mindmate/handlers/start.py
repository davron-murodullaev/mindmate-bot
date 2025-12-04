"""
Start Handler - Handles /start command and initial user onboarding
"""

from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, filters
from mindmate.i18n.loader import get_text
from mindmate.ui.keyboards import get_main_menu_keyboard


async def start_command(update, context):
    """Handle the /start command"""
    await update.message.reply_text("Handler start works! Welcome to MindMate!")


def register_start_handlers(app):
    """Register all start-related handlers"""
    app.add_handler(CommandHandler("start", start_command))
