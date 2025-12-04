"""
Menu Handler - Handles main menu navigation and menu callbacks
"""

from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, filters
from mindmate.i18n.loader import get_text
from mindmate.ui.keyboards import get_main_menu_keyboard


async def menu_command(update, context):
    """Handle the /menu command"""
    await update.message.reply_text("Handler menu works! Main menu coming soon...")


def register_menu_handlers(app):
    """Register all menu-related handlers"""
    app.add_handler(CommandHandler("menu", menu_command))
