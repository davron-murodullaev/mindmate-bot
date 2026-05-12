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
from mindmate.services.user_service import user_service
from mindmate.i18n.loader import t

logger = logging.getLogger(__name__)

_CACHE_LANG_KEY = "_cached_lang"


async def stats_admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/stats — admin-only summary of bot usage."""
    user = update.effective_user
    message = update.message
    lang = context.user_data.get(_CACHE_LANG_KEY, "en")

    if not settings.is_admin(user.id):
        await message.reply_text(t("admin.no_access", lang))
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

        conv_rate = (premium_active / total_users * 100) if total_users else 0
        msgs = t("admin.messages", lang)

        text = (
            f"{t('admin.stats_title', lang)}\n\n"
            f"{t('admin.users_header', lang)}\n"
            f"• {t('admin.total', lang)}: *{total_users}*\n"
            f"• {t('admin.new_today', lang)}: *{new_today}*\n"
            f"• {t('admin.wau', lang)}: *{active_7d}*\n"
            f"• {t('admin.mau', lang)}: *{active_30d}*\n\n"
            f"{t('admin.friends_header', lang)}\n"
            f"• {t('admin.profiles', lang)}: *{friend_profiles}*\n"
            f"• {t('admin.verified', lang)}: *{friend_verified}*\n"
            f"• {t('admin.likes', lang)}: *{friend_likes_total}*\n"
            f"• {t('admin.matches', lang)}: *{friend_matches_total}*\n\n"
            f"{t('admin.modules_header', lang)}\n"
            f"• {t('admin.exam_profiles', lang)}: *{exam_profiles}*\n"
            f"• {t('admin.career_profiles', lang)}: *{career_profiles}*\n\n"
            f"{t('admin.premium_header', lang)}\n"
            f"• {t('admin.active_subs', lang)}: *{premium_active}*\n"
            f"• {t('admin.conversion', lang)}: *{conv_rate:.1f}%*\n\n"
            f"{t('admin.ai_header', lang)}\n"
            f"• {t('admin.today', lang)}: *{ai_today}* {msgs}\n"
            f"• {t('admin.week', lang)}: *{ai_7d}* {msgs}"
        )

        await message.reply_text(text, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Error in stats_admin_handler: {e}")
        await message.reply_text(f"{t('admin.error', lang)}: {e}")
