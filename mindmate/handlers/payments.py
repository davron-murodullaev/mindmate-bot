"""
Telegram Stars (XTR currency) payment integration for Premium.

No merchant account, no API key, no Click/Payme integration needed.
Telegram handles the entire flow; we just send an invoice and react to
successful_payment + pre_checkout_query events.

Pricing model: 1-month / 3-month / 12-month Premium subscriptions.
"""
import logging
from datetime import datetime, timedelta

from telegram import (
    Update,
    LabeledPrice,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ContextTypes

from mindmate.services.user_service import user_service
from mindmate.db.queries import upsert_subscription, get_subscription, is_premium_active
from mindmate.i18n.loader import t

logger = logging.getLogger(__name__)

# Plan configuration: (plan_id, days, price_in_stars)
PLANS = [
    ("premium_1m", 30, 100),   # 100 Stars ≈ $1.99
    ("premium_3m", 90, 250),   # 250 Stars ≈ $4.99 (saves ~17%)
    ("premium_12m", 365, 800), # 800 Stars ≈ $15.99 (saves ~33%)
]

PLAN_BY_ID = {p[0]: p for p in PLANS}


def _plan_label(plan_id: str, lang: str) -> str:
    suffix = plan_id.replace("premium_", "")
    return t(f"payments.plan_{suffix}_label", lang)


def _plan_desc(plan_id: str, lang: str) -> str:
    suffix = plan_id.replace("premium_", "")
    return t(f"payments.plan_{suffix}_desc", lang)


def kb_plan_select(lang: str = "en") -> InlineKeyboardMarkup:
    rows = []
    for plan_id, _days, stars in PLANS:
        label = _plan_label(plan_id, lang)
        rows.append([InlineKeyboardButton(
            f"{label} — ⭐ {stars}",
            callback_data=f"buy_{plan_id}",
        )])
    rows.append([InlineKeyboardButton(t("buttons.back", lang), callback_data="menu_main")])
    return InlineKeyboardMarkup(rows)


async def buy_premium_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/buy_premium command — show available plans."""
    user = update.effective_user
    message = update.message
    lang = await user_service.get_user_language(user.id)
    try:
        if await is_premium_active(user.id):
            sub = await get_subscription(user.id)
            expires = sub.get("expires_at") if sub else None
            expires_str = expires.strftime("%Y-%m-%d") if expires else "—"
            await message.reply_text(
                t("payments.already_premium", lang).format(expires=expires_str),
                reply_markup=kb_plan_select(lang),
                parse_mode="Markdown",
            )
            return

        await message.reply_text(
            f"{t('payments.premium_title', lang)}\n\n"
            f"{t('payments.premium_benefits', lang)}\n\n"
            f"{t('payments.select_plan', lang)}",
            reply_markup=kb_plan_select(lang),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Error in buy_premium_handler: {e}")
        await message.reply_text(t("payments.generic_error", lang))


async def buy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """User picked a plan — send a Telegram Stars invoice."""
    query = update.callback_query
    lang = await user_service.get_user_language(query.from_user.id)
    try:
        await query.answer()
        data = query.data or ""

        if not data.startswith("buy_"):
            return
        plan_id = data.replace("buy_", "")
        plan = PLAN_BY_ID.get(plan_id)
        if not plan:
            await query.answer(t("payments.unknown_plan", lang), show_alert=True)
            return

        plan_id, _days, stars = plan
        label = _plan_label(plan_id, lang)
        description = _plan_desc(plan_id, lang)

        # Send a Telegram Stars invoice. Currency must be 'XTR' (Stars),
        # provider_token must be empty for Stars.
        await context.bot.send_invoice(
            chat_id=query.from_user.id,
            title=label,
            description=description,
            payload=plan_id,
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label=label, amount=stars)],
        )
    except Exception as e:
        logger.error(f"Error in buy_callback: {e}")
        try:
            await query.message.chat.send_message(t("payments.invoice_error", lang))
        except Exception:
            pass


async def precheckout_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Telegram asks before charging — we always approve (validation already done)."""
    query = update.pre_checkout_query
    try:
        await query.answer(ok=True)
    except Exception as e:
        logger.error(f"Pre-checkout error: {e}")
        try:
            lang = await user_service.get_user_language(query.from_user.id)
            await query.answer(ok=False, error_message=t("payments.technical_error", lang))
        except Exception:
            pass


async def successful_payment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Payment confirmed — extend the user's subscription."""
    user = update.effective_user
    message = update.message
    lang = await user_service.get_user_language(user.id)
    try:
        payment = message.successful_payment
        plan_id = payment.invoice_payload
        plan = PLAN_BY_ID.get(plan_id)
        if not plan:
            logger.error(f"Unknown plan in successful payment: {plan_id}")
            await message.reply_text(t("payments.unknown_plan_admin", lang))
            return

        _id, days, stars = plan

        # Extend from existing expiry if still valid, else from now
        sub = await get_subscription(user.id)
        if sub and sub.get("expires_at") and sub["expires_at"] > datetime.now():
            new_expiry = sub["expires_at"] + timedelta(days=days)
        else:
            new_expiry = datetime.now() + timedelta(days=days)

        await upsert_subscription(
            user_id=user.id,
            tier="premium",
            expires_at=new_expiry,
            payment_provider="telegram_stars",
            payment_id=payment.telegram_payment_charge_id,
        )

        await message.reply_text(
            t("payments.success", lang).format(
                expires=new_expiry.strftime("%Y-%m-%d"),
                stars=stars,
            ),
            parse_mode="Markdown",
        )

    except Exception as e:
        logger.error(f"Error in successful_payment_handler: {e}")
        await message.reply_text(t("payments.partial_success", lang))
