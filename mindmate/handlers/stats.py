"""
Statistics handler — simplified to mood + journal + overall.
"""
import logging

from telegram import Update
from telegram.ext import ContextTypes

from mindmate.services.user_service import user_service
from mindmate.services.stats_service import stats_service
from mindmate.ui.keyboards import get_stats_keyboard, get_back_to_menu_keyboard
from mindmate.i18n import t
from mindmate.core.constants import MOOD_EMOJIS

logger = logging.getLogger(__name__)


async def stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /stats command."""
    user = update.effective_user
    message = update.message
    try:
        lang = await user_service.get_user_language(user.id)
        await message.reply_text(
            t("stats.welcome", lang),
            reply_markup=get_stats_keyboard(lang),
        )
    except Exception as e:
        logger.error(f"Error in stats_handler: {e}")
        await message.reply_text("Statistics")


def _format_mood_stats(stats: dict, lang: str, days: int = 7) -> str:
    """Render mood stats as a tidy text block."""
    if not stats:
        return t("mood.no_data", lang)

    header = t("mood.stats", lang).format(days=days)
    lines = [header, ""]
    for mood, count in sorted(stats.items(), key=lambda x: -x[1]):
        emoji = MOOD_EMOJIS.get(mood, "")
        lines.append(f"{emoji} {mood.capitalize()}: {count}")
    return "\n".join(lines)


async def stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle stats_* callbacks."""
    query = update.callback_query
    user = query.from_user
    try:
        await query.answer()
        lang = await user_service.get_user_language(user.id)
        data = query.data or ""

        if data == "stats_mood":
            stats = await stats_service.get_mood_statistics(user.id, days=7)
            text = _format_mood_stats(stats, lang, days=7)
            await query.edit_message_text(
                text=text,
                reply_markup=get_back_to_menu_keyboard(lang),
            )

        elif data == "stats_journal":
            count = await stats_service.get_journal_count(user.id, days=30)
            text = f"📝 {count} entries (last 30 days)"
            await query.edit_message_text(
                text=text,
                reply_markup=get_back_to_menu_keyboard(lang),
            )

        elif data == "stats_overall":
            summary = await stats_service.get_overall(user.id, days=30)
            text = t("stats.summary", lang).format(
                days=30,
                moods=summary["moods"],
                journals=summary["journals"],
                chats=summary["chats"],
            )
            await query.edit_message_text(
                text=text,
                reply_markup=get_back_to_menu_keyboard(lang),
            )

    except Exception as e:
        logger.error(f"Error in stats_callback: {e}")
        try:
            await query.edit_message_text("Statistics")
        except Exception:
            pass
