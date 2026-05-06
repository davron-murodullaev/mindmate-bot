"""
Mood tracking handler
"""
import logging

from telegram import Update
from telegram.ext import ContextTypes

from mindmate.services.user_service import user_service
from mindmate.db.queries import create_mood
from mindmate.ui.keyboards import get_mood_keyboard, get_back_to_menu_keyboard
from mindmate.i18n import t
from mindmate.core.constants import EMOJI_TO_MOOD

logger = logging.getLogger(__name__)


async def mood_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /mood command."""
    user = update.effective_user
    message = update.message

    try:
        lang = await user_service.get_user_language(user.id)
        await message.reply_text(
            t("mood.select", lang),
            reply_markup=get_mood_keyboard(lang),
        )
    except Exception as e:
        logger.error(f"Error in mood_handler: {e}")
        await message.reply_text("How are you feeling today?")


async def mood_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle mood selection callback (mood_<type>)."""
    query = update.callback_query
    user = query.from_user

    try:
        await query.answer()

        lang = await user_service.get_user_language(user.id)
        mood_type = (query.data or "").replace("mood_", "").strip()

        if not mood_type:
            return

        await create_mood(user.id, mood_type)

        await query.edit_message_text(
            text=t("mood.logged", lang),
            reply_markup=get_back_to_menu_keyboard(lang),
        )

    except Exception as e:
        logger.error(f"Error in mood_callback: {e}")
        try:
            await query.edit_message_text("Mood logged successfully!")
        except Exception:
            pass


async def save_mood_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle mood emoji messages (e.g. user sends 😊).

    Looks up the leading character against EMOJI_TO_MOOD and stores the mood.
    """
    user = update.effective_user
    message = update.message

    try:
        if not message or not message.text:
            return

        first_char = message.text.strip()[0] if message.text.strip() else ""
        mood_type = EMOJI_TO_MOOD.get(first_char)
        if not mood_type:
            return  # Not a recognized mood emoji — let other handlers run

        lang = await user_service.get_user_language(user.id)
        await create_mood(user.id, mood_type)

        await message.reply_text(
            t("mood.logged", lang),
            reply_markup=get_back_to_menu_keyboard(lang),
        )

    except Exception as e:
        logger.error(f"Error in save_mood_handler: {e}")
