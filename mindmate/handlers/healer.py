"""
Healer Handler - Handles meditation guidance and healing exercises
"""

from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, filters
from mindmate.i18n.loader import get_text
from mindmate.ui.keyboards import get_main_menu_keyboard


async def healer_command(update, context):
    """Handle the /healer command"""
    await update.message.reply_text("Handler healer works! Healing exercises coming soon...")


def register_healer_handlers(app):
    """Register all healer-related handlers"""
    app.add_handler(CommandHandler("healer", healer_command))
