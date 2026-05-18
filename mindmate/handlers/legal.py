"""
/privacy and /terms commands — required for any bot that handles personal
data and especially for friend-finding / dating features.
"""
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from mindmate.services.user_service import user_service
from mindmate.i18n import t

logger = logging.getLogger(__name__)


def _privacy_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("legal.btn_terms", lang), callback_data="legal_terms")],
        [InlineKeyboardButton(t("legal.btn_main_menu", lang), callback_data="menu_main")],
    ])


def _terms_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("legal.btn_privacy", lang), callback_data="legal_privacy")],
        [InlineKeyboardButton(t("legal.btn_main_menu", lang), callback_data="menu_main")],
    ])


async def privacy_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/privacy command — show full privacy policy."""
    user = update.effective_user
    message = update.message
    lang = await user_service.get_user_language(user.id)
    try:
        await message.reply_text(
            t("legal.privacy_text", lang),
            reply_markup=_privacy_kb(lang),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Error in privacy_handler: {e}")
        await message.reply_text(t("legal.privacy_text", lang))


async def terms_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/terms command — show full terms of service."""
    user = update.effective_user
    message = update.message
    lang = await user_service.get_user_language(user.id)
    try:
        await message.reply_text(
            t("legal.terms_text", lang),
            reply_markup=_terms_kb(lang),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Error in terms_handler: {e}")
        await message.reply_text(t("legal.terms_text", lang))


async def legal_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle legal_* callbacks (switch between privacy and terms views)."""
    query = update.callback_query
    lang = await user_service.get_user_language(query.from_user.id)
    try:
        await query.answer()
        data = query.data or ""
        if data == "legal_privacy":
            await query.edit_message_text(
                t("legal.privacy_text", lang),
                reply_markup=_privacy_kb(lang),
                parse_mode="Markdown",
            )
        elif data == "legal_terms":
            await query.edit_message_text(
                t("legal.terms_text", lang),
                reply_markup=_terms_kb(lang),
                parse_mode="Markdown",
            )
    except Exception as e:
        logger.error(f"Error in legal_callback: {e}")
