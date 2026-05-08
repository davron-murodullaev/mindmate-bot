"""
Profile hub handler — central place for the user's personal tools.

Wraps mood, journal, reminders, stats, healer, productivity, settings, premium
under one cleaner sub-menu so the main menu stays uncluttered.
"""
import logging

from telegram import Update
from telegram.ext import ContextTypes

from mindmate.services.user_service import user_service
from mindmate.db.queries import (
    get_subscription,
    is_premium_active,
    get_exam_profile,
    get_career_profile,
)
from mindmate.ui.keyboards import get_profile_menu_keyboard
from mindmate.i18n import t

logger = logging.getLogger(__name__)


async def profile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the profile hub with a personalized header."""
    user = update.effective_user
    chat = update.effective_chat
    try:
        lang = await user_service.get_user_language(user.id)
        text = await _build_profile_text(user.id, user.first_name, lang)
        await chat.send_message(
            text,
            reply_markup=get_profile_menu_keyboard(lang),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Error in profile_handler: {e}")
        await chat.send_message("Profile")


async def profile_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Open the profile hub from a callback (menu_profile)."""
    query = update.callback_query
    user = query.from_user
    try:
        await query.answer()
        lang = await user_service.get_user_language(user.id)
        text = await _build_profile_text(user.id, user.first_name, lang)
        await query.edit_message_text(
            text,
            reply_markup=get_profile_menu_keyboard(lang),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Error in profile_callback: {e}")
        try:
            await query.edit_message_text("Profile")
        except Exception:
            pass


async def _build_profile_text(user_id: int, first_name: str, lang: str) -> str:
    """Build a personalized profile header showing key facts."""
    is_pro = await is_premium_active(user_id)
    exam = await get_exam_profile(user_id)
    career = await get_career_profile(user_id)

    name = first_name or "do'st"

    badges = []
    if is_pro:
        badges.append("💎 Premium")
    if exam:
        badges.append("🎓 Imtihon Mentor")
    if career:
        badges.append("💼 Karyera Coach")

    badge_str = " · ".join(badges) if badges else "_yangi foydalanuvchi_"

    if lang == "ru":
        title = f"👤 *Профиль: {name}*"
    elif lang == "en":
        title = f"👤 *{name}'s Profile*"
    else:
        title = f"👤 *{name} ning profili*"

    return (
        f"{title}\n"
        f"{badge_str}\n\n"
        f"_{t('profile.subtitle', lang)}_"
    )
