"""
Start command handler.

Behavior:
- New user (no language set yet) → ask to choose language
- Returning user → greet and open the main menu directly
"""
import logging

from telegram import Update
from telegram.ext import ContextTypes

from mindmate.services.user_service import user_service
from mindmate.db.queries import get_user
from mindmate.ui.keyboards import (
    get_language_keyboard,
    get_setup_keyboard,
    get_main_menu_keyboard,
)
from mindmate.i18n import t
from mindmate.core.constants import SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE

logger = logging.getLogger(__name__)


def _clear_all_wizard_state(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear every transient wizard/mode state from user_data.

    Called by /start and /cancel so commands always reset the user back to
    a clean main-menu state regardless of where they were stuck.
    """
    for key in (
        "mode",
        "waiting_for_journal",
        "waiting_for_reminder",
        "exam_setup",
        "exam_edit",
        "career_setup",
        "career_edit",
        "career_action",
        "interview_question",
        "last_practice_question",
        "friends_setup",
        "friends_edit_photos_state",
        "friends_pref_age",
        "friends_verify",
        "browsing_candidate_id",
    ):
        context.user_data.pop(key, None)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start — greet returning users; onboard new users."""
    user = update.effective_user
    message = update.message

    # /start always resets — users use it as an "escape hatch"
    _clear_all_wizard_state(context)

    try:
        # Check whether the user already exists in the DB
        existing = await get_user(user.id)
        is_returning = bool(existing)

        # Always upsert (refresh names) but pass existing language if any
        await user_service.get_or_create_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
        )

        if is_returning and existing.get("language_code") in SUPPORTED_LANGUAGES:
            # Returning user — straight to main menu in their language
            lang = existing["language_code"]
            name = user.first_name or ""
            greeting_key = "start.welcome_back"
            try:
                greeting = t(greeting_key, lang).format(name=name)
            except Exception:
                greeting = f"👋 {name}!"

            await message.reply_text(
                greeting,
                reply_markup=get_main_menu_keyboard(lang),
                parse_mode="Markdown",
            )
            return

        # New user (or unknown language) — ask to pick a language
        lang = (existing or {}).get("language_code") or DEFAULT_LANGUAGE
        await message.reply_text(
            t("welcome", lang),
            reply_markup=get_language_keyboard(),
            parse_mode="Markdown",
        )

    except Exception as e:
        logger.error(f"Error in start_handler: {e}")
        await message.reply_text(
            "Welcome to MindMate! Please select your language:",
            reply_markup=get_language_keyboard(),
        )


async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle language selection callback."""
    query = update.callback_query
    user = query.from_user

    try:
        await query.answer()
        raw_lang = (query.data or "").replace("lang_", "").strip().lower()
        lang = raw_lang if raw_lang in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE

        await user_service.set_user_language(user.id, lang)
        # Invalidate the session-level language cache so next requests use the new lang
        context.user_data.pop("_cached_lang", None)

        await query.edit_message_text(
            text=t("setup.complete", lang),
            reply_markup=get_setup_keyboard(lang),
        )

    except Exception as e:
        logger.error(f"Error in language_callback: {e}")
        try:
            await query.edit_message_text("Language updated!")
        except Exception:
            pass


async def setup_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle setup completion callback."""
    query = update.callback_query
    user = query.from_user

    try:
        await query.answer()
        lang = await user_service.get_user_language(user.id)

        await query.edit_message_text(
            text=t("menu.main_menu", lang),
            reply_markup=get_main_menu_keyboard(lang),
            parse_mode="Markdown",
        )

    except Exception as e:
        logger.error(f"Error in setup_callback: {e}")
        try:
            await query.edit_message_text("Welcome! What would you like to do?")
        except Exception:
            pass


async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /cancel — escape hatch from any wizard back to the main menu."""
    user = update.effective_user
    message = update.message
    try:
        _clear_all_wizard_state(context)
        context.user_data.pop("_cached_lang", None)
        lang = await user_service.get_user_language(user.id)
        await message.reply_text(
            t("general.cancel_done", lang) + "\n\n" + t("menu.main_menu", lang),
            reply_markup=get_main_menu_keyboard(lang),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Error in cancel_handler: {e}")
        await message.reply_text(t("general.cancel_done", "en"))
