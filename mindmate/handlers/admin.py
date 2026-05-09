"""
Admin commands.

/stats — overview of users, profiles, matches, premium, daily activity.
        Restricted to ADMIN_USER_IDS in settings.
"""
import logging

from telegram import Update
from telegram.ext import ContextTypes

from mindmate.core.config import settings
from mindmate.db.connection import execute_fetchrow, execute_fetchval

logger = logging.getLogger(__name__)


async def stats_admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/stats — admin-only summary of bot usage."""
    user = update.effective_user
    message = update.message

    if not settings.is_admin(user.id):
        await message.reply_text("⛔ Bu komanda faqat adminlar uchun.")
        return

    try:
        # Pull all numbers in parallel-friendly individual queries
        total_users = await execute_fetchval("SELECT COUNT(*) FROM users")
        new_today = await execute_fetchval(
            "SELECT COUNT(*) FROM users WHERE created_at >= CURRENT_DATE"
        )
        active_7d = await execute_fetchval(
            "SELECT COUNT(*) FROM users WHERE last_active >= NOW() - INTERVAL '7 days'"
        )
        active_30d = await execute_fetchval(
            "SELECT COUNT(*) FROM users WHERE last_active >= NOW() - INTERVAL '30 days'"
        )

        friend_profiles = await execute_fetchval(
            "SELECT COUNT(*) FROM friend_profiles WHERE is_active = true"
        )
        friend_verified = await execute_fetchval(
            "SELECT COUNT(*) FROM photo_verifications WHERE is_verified = true"
        )
        friend_likes_total = await execute_fetchval(
            "SELECT COUNT(*) FROM friend_likes WHERE is_like = true"
        )
        friend_matches_total = await execute_fetchval(
            "SELECT COUNT(*) FROM friend_matches"
        )

        exam_profiles = await execute_fetchval("SELECT COUNT(*) FROM exam_profiles")
        career_profiles = await execute_fetchval("SELECT COUNT(*) FROM career_profiles")

        premium_active = await execute_fetchval(
            "SELECT COUNT(*) FROM subscriptions "
            "WHERE tier = 'premium' AND (expires_at IS NULL OR expires_at > NOW())"
        )

        ai_today = await execute_fetchval(
            "SELECT COALESCE(SUM(ai_messages), 0) FROM daily_usage "
            "WHERE usage_date = CURRENT_DATE"
        )
        ai_7d = await execute_fetchval(
            "SELECT COALESCE(SUM(ai_messages), 0) FROM daily_usage "
            "WHERE usage_date >= CURRENT_DATE - INTERVAL '7 days'"
        )

        # Conversion rate
        conv_rate = (premium_active / total_users * 100) if total_users else 0

        text = (
            f"📊 *MindMate Statistikasi*\n\n"
            f"*👥 Foydalanuvchilar*\n"
            f"• Jami: *{total_users}*\n"
            f"• Bugun yangi: *{new_today}*\n"
            f"• 7 kun faol (WAU): *{active_7d}*\n"
            f"• 30 kun faol (MAU): *{active_30d}*\n\n"
            f"*💝 Do'st topish*\n"
            f"• Anketa: *{friend_profiles}*\n"
            f"• Tasdiqlangan: *{friend_verified}*\n"
            f"• Like'lar: *{friend_likes_total}*\n"
            f"• Match'lar: *{friend_matches_total}*\n\n"
            f"*🎓 Boshqa modullar*\n"
            f"• Imtihon Mentor: *{exam_profiles}*\n"
            f"• Karyera Coach: *{career_profiles}*\n\n"
            f"*💎 Premium*\n"
            f"• Faol obuna: *{premium_active}*\n"
            f"• Konvertatsiya: *{conv_rate:.1f}%*\n\n"
            f"*🤖 AI ishlatilishi*\n"
            f"• Bugun: *{ai_today}* xabar\n"
            f"• 7 kun: *{ai_7d}* xabar"
        )

        await message.reply_text(text, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Error in stats_admin_handler: {e}")
        await message.reply_text(f"❌ Xatolik: {e}")
