"""
Fitness tracking handler
"""
from telegram import Update
from telegram.ext import ContextTypes
import logging
import re

from mindmate.services.user_service import user_service
from mindmate.services.workout_service import workout_service
from mindmate.ui.keyboards import get_fitness_keyboard, get_back_to_menu_keyboard
from mindmate.ui.layouts import format_workout_stats
from mindmate.i18n import t

logger = logging.getLogger(__name__)


async def fitness_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /fitness command."""
    user = update.effective_user
    message = update.message

    try:
        lang = await user_service.get_user_language(user.id)

        await message.reply_text(
            t("fitness.welcome", lang),
            reply_markup=get_fitness_keyboard(lang)
        )

    except Exception as e:
        logger.error(f"Error in fitness_handler: {e}")
        await message.reply_text("Fitness Tracking")


async def fitness_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle fitness callback."""
    query = update.callback_query
    user = query.from_user

    try:
        await query.answer()

        lang = await user_service.get_user_language(user.id)

        if query.data == "fitness_log":
            await query.edit_message_text(
                text=t("fitness.enter_workout", lang)
            )
            context.user_data['waiting_for_workout'] = True

        elif query.data == "fitness_stats":
            stats = await workout_service.get_stats(user.id, days=7)
            stats_text = format_workout_stats(stats, lang, days=7)
            await query.edit_message_text(
                text=stats_text,
                reply_markup=get_back_to_menu_keyboard(lang)
            )

    except Exception as e:
        logger.error(f"Error in fitness_callback: {e}")
        await query.edit_message_text("Fitness menu")


async def log_workout_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle workout logging from text message."""
    user = update.effective_user
    message = update.message

    try:
        if not context.user_data.get('waiting_for_workout'):
            return

        text = message.text
        lang = await user_service.get_user_language(user.id)

        # Parse workout: "Activity: duration"
        match = re.match(r'(.+?):\s*(\d+)', text)
        if match:
            activity = match.group(1).strip()
            duration = int(match.group(2))

            # Log workout
            await workout_service.log_workout(user.id, activity, duration)

            await message.reply_text(
                t("fitness.logged", lang, activity=activity, duration=duration),
                reply_markup=get_back_to_menu_keyboard(lang)
            )

            context.user_data['waiting_for_workout'] = False
        else:
            await message.reply_text(t("errors.invalid_input", lang))

    except Exception as e:
        logger.error(f"Error in log_workout_handler: {e}")
        await message.reply_text("Error logging workout")
