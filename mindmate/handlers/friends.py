"""
Friends-finding feature placeholder.

Full feature (anketa, swipe, AI matchmaker, audio intro, voice verification)
is described in product roadmap; this handler shows a "coming soon" page so
the menu item exists from day one and we can capture interest.
"""
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from mindmate.services.user_service import user_service
from mindmate.i18n import t

logger = logging.getLogger(__name__)

# Simple in-memory waitlist signal — for now we just log it. A real waitlist
# table can be added later if we want to track interest.
_WAITLIST_LOG = set()


async def friends_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Entry point for the friends-finding feature (currently teaser)."""
    user = update.effective_user
    chat = update.effective_chat
    try:
        lang = await user_service.get_user_language(user.id)
        await chat.send_message(
            _teaser_text(lang),
            reply_markup=_teaser_keyboard(user.id, lang),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Error in friends_handler: {e}")
        await chat.send_message("Coming soon")


async def friends_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle friends_* callbacks."""
    query = update.callback_query
    user = query.from_user
    try:
        await query.answer()
        lang = await user_service.get_user_language(user.id)
        data = query.data or ""

        if data == "menu_friends":
            await query.edit_message_text(
                _teaser_text(lang),
                reply_markup=_teaser_keyboard(user.id, lang),
                parse_mode="Markdown",
            )
            return

        if data == "friends_waitlist":
            _WAITLIST_LOG.add(user.id)
            logger.info(f"User {user.id} joined friends waitlist (total: {len(_WAITLIST_LOG)})")
            await query.edit_message_text(
                t("friends.waitlist_joined", lang),
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(t("buttons.back", lang), callback_data="menu_main"),
                ]]),
                parse_mode="Markdown",
            )
            return

    except Exception as e:
        logger.error(f"Error in friends_callback: {e}")
        try:
            await query.edit_message_text("Coming soon")
        except Exception:
            pass


def _teaser_text(lang: str) -> str:
    return t("friends.teaser", lang)


def _teaser_keyboard(user_id: int, lang: str) -> InlineKeyboardMarkup:
    in_waitlist = user_id in _WAITLIST_LOG
    if in_waitlist:
        rows = [[InlineKeyboardButton(t("friends.in_waitlist", lang), callback_data="menu_main")]]
    else:
        rows = [[InlineKeyboardButton(t("friends.join_waitlist", lang), callback_data="friends_waitlist")]]
    rows.append([InlineKeyboardButton(t("buttons.back", lang), callback_data="menu_main")])
    return InlineKeyboardMarkup(rows)
