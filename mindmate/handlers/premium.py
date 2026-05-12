"""
Premium subscription handler (placeholder — wire real payments later).

This handler shows the subscription page and acknowledges Stars/Card buttons.
Actual payment integration (Telegram Stars invoices, Click/Payme/Stripe) must
be wired in by the bot owner — see manual tasks list.
"""
import logging

from telegram import Update
from telegram.ext import ContextTypes

from mindmate.services.user_service import user_service
from mindmate.db.queries import get_subscription, is_premium_active
from mindmate.ui.keyboards import get_premium_keyboard, get_back_to_menu_keyboard
from mindmate.i18n import t

logger = logging.getLogger(__name__)


async def premium_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /premium command."""
    user = update.effective_user
    message = update.message
    try:
        lang = await user_service.get_user_language(user.id)
        if await is_premium_active(user.id):
            sub = await get_subscription(user.id)
            expires = sub.get("expires_at") if sub else None
            expires_str = expires.strftime("%Y-%m-%d") if expires else "—"
            await message.reply_text(
                t("premium.active", lang).format(date=expires_str),
                reply_markup=get_back_to_menu_keyboard(lang),
            )
        else:
            await message.reply_text(
                t("premium.welcome", lang),
                reply_markup=get_premium_keyboard(lang),
            )
    except Exception as e:
        logger.error(f"Error in premium_handler: {e}")
        await message.reply_text("Premium")


async def premium_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle premium_* callbacks — opens the Stars plan picker."""
    query = update.callback_query
    user = query.from_user
    try:
        await query.answer()
        lang = await user_service.get_user_language(user.id)
        data = query.data or ""

        if data == "premium_stars":
            # Show the Stars plan picker (1m / 3m / 12m)
            from mindmate.handlers.payments import kb_plan_select
            await query.edit_message_text(
                text=(
                    f"{t('payments.stars_payment_title', lang)}\n\n"
                    f"{t('payments.stars_payment_prompt', lang)}"
                ),
                reply_markup=kb_plan_select(lang),
                parse_mode="Markdown",
            )

        elif data == "premium_card":
            await query.edit_message_text(
                text=t("payments.card_coming_soon", lang),
                reply_markup=get_back_to_menu_keyboard(lang),
                parse_mode="Markdown",
            )

    except Exception as e:
        logger.error(f"Error in premium_callback: {e}")
        try:
            await query.edit_message_text("Premium")
        except Exception:
            pass
