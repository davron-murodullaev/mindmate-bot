"""
Statistics handler
"""
from telegram import Update
from telegram.ext import ContextTypes
import logging

from mindmate.services.user_service import user_service
from mindmate.services.stats_service import stats_service
from mindmate.ui.keyboards import get_stats_keyboard, get_back_to_menu_keyboard
from mindmate.ui.layouts import (
    format_mood_stats,
    format_workout_stats,
    format_meditation_stats,
    format_finance_stats
)
from mindmate.i18n import t

logger = logging.getLogger(__name__)


async def stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /stats command."""
    user = update.effective_user
    message = update.message

    try:
        lang = await user_service.get_user_language(user.id)

        await message.reply_text(
            t("stats.welcome", lang),
            reply_markup=get_stats_keyboard(lang)
        )

    except Exception as e:
        logger.error(f"Error in stats_handler: {e}")
        await message.reply_text("Statistics")


async def stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle stats callback."""
    query = update.callback_query
    user = query.from_user

    try:
        await query.answer()

        lang = await user_service.get_user_language(user.id)

        if query.data == "stats_mood":
            stats = await stats_service.get_mood_statistics(user.id, days=7)
            stats_text = format_mood_stats(stats, lang, days=7)
            await query.edit_message_text(
                text=stats_text,
                reply_markup=get_back_to_menu_keyboard(lang)
            )

        elif query.data == "stats_fitness":
            stats = await stats_service.get_fitness_statistics(user.id, days=7)
            stats_text = format_workout_stats(stats, lang, days=7)
            await query.edit_message_text(
                text=stats_text,
                reply_markup=get_back_to_menu_keyboard(lang)
            )

        elif query.data == "stats_meditation":
            stats = await stats_service.get_meditation_statistics(user.id, days=30)
            stats_text = format_meditation_stats(stats, lang)
            await query.edit_message_text(
                text=stats_text,
                reply_markup=get_back_to_menu_keyboard(lang)
            )

        elif query.data == "stats_finance":
            stats = await stats_service.get_finance_statistics(user.id, days=30)
            stats_text = format_finance_stats(stats, lang, days=30)
            await query.edit_message_text(
                text=stats_text,
                reply_markup=get_back_to_menu_keyboard(lang)
            )

    except Exception as e:
        logger.error(f"Error in stats_callback: {e}")
        await query.edit_message_text("Statistics")
