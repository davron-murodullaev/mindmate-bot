"""
Fitness Handler - Handles workout logging and fitness tracking
"""

from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, filters
from mindmate.i18n.loader import get_text
from mindmate.ui.keyboards import get_main_menu_keyboard


async def fitness_command(update, context):
    """Handle the /fitness command"""
    await update.message.reply_text("Handler fitness works! Fitness tracking coming soon...")


def register_fitness_handlers(app):
    """Register all fitness-related handlers"""
    app.add_handler(CommandHandler("fitness", fitness_command))
