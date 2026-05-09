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

logger = logging.getLogger(__name__)


# Plan configuration: (plan_id, label, days, price_in_stars, description)
PLANS = [
    (
        "premium_1m",
        "💎 Premium — 1 oy",
        30,
        100,  # 100 Stars ≈ $1.99
        "1 oylik MindMate Premium",
    ),
    (
        "premium_3m",
        "💎 Premium — 3 oy",
        90,
        250,  # 250 Stars ≈ $4.99 (saves ~17%)
        "3 oylik MindMate Premium (17% chegirma)",
    ),
    (
        "premium_12m",
        "💎 Premium — 12 oy",
        365,
        800,  # 800 Stars ≈ $15.99 (saves ~33%)
        "12 oylik MindMate Premium (33% chegirma)",
    ),
]

PLAN_BY_ID = {p[0]: p for p in PLANS}


def kb_plan_select() -> InlineKeyboardMarkup:
    """Show all premium plan options."""
    rows = []
    for plan_id, label, _days, stars, _desc in PLANS:
        rows.append([InlineKeyboardButton(
            f"{label} — ⭐ {stars}",
            callback_data=f"buy_{plan_id}",
        )])
    rows.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="menu_main")])
    return InlineKeyboardMarkup(rows)


async def buy_premium_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/buy_premium command — show available plans."""
    user = update.effective_user
    message = update.message
    try:
        if await is_premium_active(user.id):
            sub = await get_subscription(user.id)
            expires = sub.get("expires_at") if sub else None
            expires_str = expires.strftime("%Y-%m-%d") if expires else "—"
            await message.reply_text(
                f"✅ *Sizda allaqachon Premium bor!*\n\n"
                f"Tugash sanasi: *{expires_str}*\n\n"
                f"Yana bir muddat qo'shmoqchimisiz? Quyidagi rejalarni tanlang:",
                reply_markup=kb_plan_select(),
                parse_mode="Markdown",
            )
            return

        await message.reply_text(
            "💎 *MindMate Premium*\n\n"
            "*Premium afzalliklari:*\n"
            "✅ Cheksiz AI suhbatlar\n"
            "✅ Cheksiz eslatmalar va kundalik\n"
            "✅ Do'st topish: cheksiz like\n"
            "✅ Sizni yoqtirgan odamlarni ko'rish\n"
            "✅ Premium nishon (✨)\n"
            "✅ Birinchi navbatda javob\n\n"
            "*Rejani tanlang:*",
            reply_markup=kb_plan_select(),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Error in buy_premium_handler: {e}")
        await message.reply_text("❌ Xatolik yuz berdi.")


async def buy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """User picked a plan — send a Telegram Stars invoice."""
    query = update.callback_query
    user = query.from_user
    try:
        await query.answer()
        data = query.data or ""

        if not data.startswith("buy_"):
            return
        plan_id = data.replace("buy_", "")
        plan = PLAN_BY_ID.get(plan_id)
        if not plan:
            await query.answer("❌ Noma'lum reja", show_alert=True)
            return

        plan_id, label, days, stars, description = plan

        # Send a Telegram Stars invoice. Currency must be 'XTR' (Stars),
        # provider_token must be empty for Stars.
        await context.bot.send_invoice(
            chat_id=user.id,
            title=label,
            description=description,
            payload=plan_id,        # Identifies the plan in successful_payment
            provider_token="",      # Empty for Stars
            currency="XTR",
            prices=[LabeledPrice(label=label, amount=stars)],
        )
    except Exception as e:
        logger.error(f"Error in buy_callback: {e}")
        try:
            await query.message.chat.send_message(
                "❌ To'lov rejasini yuborishda xatolik. Qaytadan urinib ko'ring."
            )
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
            await query.answer(ok=False, error_message="Texnik xatolik. Qaytadan urinib ko'ring.")
        except Exception:
            pass


async def successful_payment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Payment confirmed — extend the user's subscription."""
    user = update.effective_user
    message = update.message
    try:
        payment = message.successful_payment
        plan_id = payment.invoice_payload
        plan = PLAN_BY_ID.get(plan_id)
        if not plan:
            logger.error(f"Unknown plan in successful payment: {plan_id}")
            await message.reply_text("❌ Noma'lum reja. Adminga murojaat qiling.")
            return

        _id, label, days, stars, _desc = plan

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
            f"🎉 *Premium faollashtirildi!*\n\n"
            f"📅 Tugash sanasi: *{new_expiry.strftime('%Y-%m-%d')}*\n"
            f"⭐ To'langan: *{stars} Stars*\n\n"
            f"Endi cheksiz AI suhbatlari, cheksiz like'lar va boshqa imkoniyatlardan "
            f"foydalanishingiz mumkin. Rahmat! 💎",
            parse_mode="Markdown",
        )

    except Exception as e:
        logger.error(f"Error in successful_payment_handler: {e}")
        await message.reply_text(
            "✅ To'lov muvaffaqiyatli, ammo tizimda kichik xato. "
            "Adminga murojaat qiling — Premium qo'lda yoqiladi."
        )
