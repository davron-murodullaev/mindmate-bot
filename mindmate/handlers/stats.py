"""
Stats Handler - Handles statistics display, charts, and reports
"""

from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, filters
from mindmate.i18n.loader import get_text
from mindmate.ui.keyboards import get_main_menu_keyboard


async def stats_command(update, context):
    """Handle the /stats command"""
    await update.message.reply_text("Handler stats works! Statistics and reports coming soon...")


def register_stats_handlers(app):
    """Register all stats-related handlers"""
    app.add_handler(CommandHandler("stats", stats_command))
