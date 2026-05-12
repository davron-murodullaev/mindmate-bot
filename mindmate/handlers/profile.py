"""
Profile hub handler.

Shows the user's configured exam, career, and friends profiles with quick-edit
buttons. Also provides access to healer, productivity, settings, and premium.
"""
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from mindmate.services.user_service import user_service
from mindmate.db.queries import (
    is_premium_active,
    get_exam_profile,
    get_career_profile,
    get_friend_profile,
)
from mindmate.ui.keyboards import get_profile_menu_keyboard
from mindmate.i18n import t
from mindmate.core.constants import (
    EXAM_TYPE_LABELS_UZ,
    EXAM_LEVEL_LABELS_UZ,
    CAREER_STATUS_LABELS_UZ,
    DTM_SUBJECT_LABELS_UZ,
)

logger = logging.getLogger(__name__)


def _profile_keyboard(lang: str, has_exam: bool, has_career: bool, has_friends: bool) -> InlineKeyboardMarkup:
    """Build profile keyboard with edit buttons for each configured section."""
    rows = []

    # Exam section
    if has_exam:
        rows.append([
            InlineKeyboardButton("🎓 Imtihon sozlamalari", callback_data="profile_view_exam"),
            InlineKeyboardButton("✏️ Tahrirlash", callback_data="profile_edit_exam"),
        ])
    else:
        rows.append([InlineKeyboardButton("🎓 Imtihon Mentor — Sozlash", callback_data="menu_exam")])

    # Career section
    if has_career:
        rows.append([
            InlineKeyboardButton("💼 Karyera sozlamalari", callback_data="profile_view_career"),
            InlineKeyboardButton("✏️ Tahrirlash", callback_data="profile_edit_career"),
        ])
    else:
        rows.append([InlineKeyboardButton("💼 Karyera Coach — Sozlash", callback_data="menu_career")])

    # Friends section
    if has_friends:
        rows.append([
            InlineKeyboardButton("💝 Do'stlik profili", callback_data="profile_view_friends"),
            InlineKeyboardButton("✏️ Tahrirlash", callback_data="profile_edit_friends"),
        ])
    else:
        rows.append([InlineKeyboardButton("💝 Do'st topish — Sozlash", callback_data="menu_friends")])

    # Spacer
    rows.append([
        InlineKeyboardButton(t("menu.healer", lang), callback_data="menu_healer"),
        InlineKeyboardButton(t("menu.productivity", lang), callback_data="menu_productivity"),
    ])
    rows.append([
        InlineKeyboardButton(t("menu.settings", lang), callback_data="menu_settings"),
        InlineKeyboardButton(t("menu.premium", lang), callback_data="menu_premium"),
    ])
    rows.append([InlineKeyboardButton(t("buttons.back", lang), callback_data="menu_main")])

    return InlineKeyboardMarkup(rows)


async def _build_profile_text(user_id: int, first_name: str, lang: str) -> str:
    """Build a personalized profile page showing all configured sections."""
    is_pro = await is_premium_active(user_id)
    exam = await get_exam_profile(user_id)
    career = await get_career_profile(user_id)
    friends = await get_friend_profile(user_id)

    name = first_name or "Do'st"
    badge = "💎 Premium" if is_pro else "🆓 Bepul"

    lines = [f"👤 *{name}ning profili* — {badge}\n"]

    # Exam section
    if exam and exam.get("exam_type"):
        exam_type = EXAM_TYPE_LABELS_UZ.get(exam["exam_type"], exam["exam_type"])
        level = EXAM_LEVEL_LABELS_UZ.get(exam.get("current_level", ""), "–")
        subjects = exam.get("subjects") or []
        subj_str = ", ".join(DTM_SUBJECT_LABELS_UZ.get(s, s) for s in subjects[:3])
        if len(subjects) > 3:
            subj_str += f" +{len(subjects)-3}"
        lines.append(f"🎓 *Imtihon:* {exam_type} · {level}")
        if subj_str:
            lines.append(f"   Fanlar: {subj_str}")
        if exam.get("exam_date"):
            from datetime import date
            delta = (exam["exam_date"] - date.today()).days
            lines.append(f"   Sanasi: {exam['exam_date']} ({delta} kun qoldi)" if delta > 0 else f"   Sanasi: {exam['exam_date']}")

    # Career section
    if career and career.get("status"):
        status = CAREER_STATUS_LABELS_UZ.get(career["status"], career["status"])
        role = career.get("target_role") or "–"
        lines.append(f"💼 *Karyera:* {status}")
        if career.get("target_role"):
            lines.append(f"   Maqsad: {role}")

    # Friends section
    if friends and friends.get("display_name"):
        looking = friends.get("looking_for", "–")
        verified = "✅ Tasdiqlangan" if friends.get("is_verified") else "⏳ Tasdiqlanmagan"
        lines.append(f"💝 *Do'stlik:* {friends['display_name']} · {verified}")
        lines.append(f"   Maqsad: {looking}")

    if len(lines) == 2:
        lines.append("_Hali hech narsa sozlanmagan. Quyidagi tugmalardan birini tanlang._")

    return "\n".join(lines)


async def profile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the profile hub."""
    user = update.effective_user
    chat = update.effective_chat
    try:
        lang = await user_service.get_user_language(user.id)
        exam = await get_exam_profile(user.id)
        career = await get_career_profile(user.id)
        friends = await get_friend_profile(user.id)
        text = await _build_profile_text(user.id, user.first_name, lang)
        await chat.send_message(
            text,
            reply_markup=_profile_keyboard(
                lang,
                has_exam=bool(exam and exam.get("exam_type")),
                has_career=bool(career and career.get("status")),
                has_friends=bool(friends and friends.get("display_name")),
            ),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Error in profile_handler: {e}")
        await chat.send_message("Profile")


async def profile_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Open the profile hub from a callback."""
    query = update.callback_query
    user = query.from_user
    try:
        await query.answer()
        lang = await user_service.get_user_language(user.id)
        exam = await get_exam_profile(user.id)
        career = await get_career_profile(user.id)
        friends = await get_friend_profile(user.id)
        text = await _build_profile_text(user.id, user.first_name, lang)
        await query.edit_message_text(
            text,
            reply_markup=_profile_keyboard(
                lang,
                has_exam=bool(exam and exam.get("exam_type")),
                has_career=bool(career and career.get("status")),
                has_friends=bool(friends and friends.get("display_name")),
            ),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Error in profile_callback: {e}")
        try:
            await query.edit_message_text("Profile")
        except Exception:
            pass


async def profile_view_exam(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show full exam profile detail."""
    query = update.callback_query
    user = query.from_user
    try:
        await query.answer()
        lang = await user_service.get_user_language(user.id)
        exam = await get_exam_profile(user.id)
        if not exam:
            await query.answer("Imtihon profili topilmadi.", show_alert=True)
            return

        from datetime import date
        exam_type = EXAM_TYPE_LABELS_UZ.get(exam.get("exam_type", ""), "–")
        level = EXAM_LEVEL_LABELS_UZ.get(exam.get("current_level", ""), "–")
        subjects = exam.get("subjects") or []
        subj_str = "\n   ".join(f"• {DTM_SUBJECT_LABELS_UZ.get(s, s)}" for s in subjects) or "kiritilmagan"
        exam_date = exam.get("exam_date")
        date_str = str(exam_date) if exam_date else "kiritilmagan"
        if exam_date:
            delta = (exam_date - date.today()).days
            date_str += f" ({delta} kun qoldi)" if delta > 0 else " (o'tgan)"
        hours = exam.get("daily_study_hours", 4)

        text = (
            f"🎓 *Imtihon Profili*\n\n"
            f"📌 Imtihon turi: {exam_type}\n"
            f"🎯 Daraja: {level}\n"
            f"📚 Fanlar:\n   {subj_str}\n"
            f"📅 Imtihon sanasi: {date_str}\n"
            f"⏱ Kunlik o'qish: {hours} soat"
        )
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✏️ Tahrirlash", callback_data="profile_edit_exam")],
                [InlineKeyboardButton(t("buttons.back", lang), callback_data="menu_profile")],
            ]),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"profile_view_exam error: {e}")


async def profile_view_career(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show full career profile detail."""
    query = update.callback_query
    user = query.from_user
    try:
        await query.answer()
        lang = await user_service.get_user_language(user.id)
        career = await get_career_profile(user.id)
        if not career:
            await query.answer("Karyera profili topilmadi.", show_alert=True)
            return

        status = CAREER_STATUS_LABELS_UZ.get(career.get("status", ""), "–")
        role = career.get("target_role") or "kiritilmagan"
        industry = career.get("industry") or "kiritilmagan"
        exp = career.get("experience_years", 0)
        skills = career.get("skills") or []
        skills_str = ", ".join(skills[:5]) if skills else "kiritilmagan"

        text = (
            f"💼 *Karyera Profili*\n\n"
            f"📊 Holat: {status}\n"
            f"🎯 Maqsad lavozim: {role}\n"
            f"🏭 Soha: {industry}\n"
            f"⏱ Tajriba: {exp} yil\n"
            f"🛠 Ko'nikmalar: {skills_str}"
        )
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✏️ Tahrirlash", callback_data="profile_edit_career")],
                [InlineKeyboardButton(t("buttons.back", lang), callback_data="menu_profile")],
            ]),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"profile_view_career error: {e}")


async def profile_view_friends(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show friends profile detail."""
    query = update.callback_query
    user = query.from_user
    try:
        await query.answer()
        lang = await user_service.get_user_language(user.id)
        friends = await get_friend_profile(user.id)
        if not friends:
            await query.answer("Do'stlik profili topilmadi.", show_alert=True)
            return

        from mindmate.core.constants import FRIEND_LOOKING_LABELS_UZ, FRIEND_INTERESTS_LABELS_UZ
        name = friends.get("display_name", "–")
        age = friends.get("age", "–")
        gender = friends.get("gender", "–")
        city = friends.get("city") or "kiritilmagan"
        looking = FRIEND_LOOKING_LABELS_UZ.get(friends.get("looking_for", ""), friends.get("looking_for", "–"))
        interests = friends.get("interests") or []
        interests_str = ", ".join(FRIEND_INTERESTS_LABELS_UZ.get(i, i) for i in interests[:5])
        bio = friends.get("bio") or "kiritilmagan"
        verified = "✅ Tasdiqlangan" if friends.get("is_verified") else "⏳ Tasdiqlanmagan"
        active = "👁 Ko'rinmoqda" if friends.get("is_active") else "🙈 Yashirilgan"

        text = (
            f"💝 *Do'stlik Profili*\n\n"
            f"👤 Ism: {name}\n"
            f"🎂 Yosh: {age}\n"
            f"👥 Jins: {gender}\n"
            f"📍 Shahar: {city}\n"
            f"🎯 Maqsad: {looking}\n"
            f"🎵 Qiziqishlar: {interests_str or 'kiritilmagan'}\n"
            f"📝 Bio: _{bio}_\n"
            f"🛡 Holat: {verified} · {active}"
        )
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✏️ Tahrirlash", callback_data="profile_edit_friends")],
                [InlineKeyboardButton(t("buttons.back", lang), callback_data="menu_profile")],
            ]),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"profile_view_friends error: {e}")


async def profile_action_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle profile_* callbacks: view/edit for exam, career, friends."""
    query = update.callback_query
    data = query.data or ""

    if data == "profile_view_exam":
        await profile_view_exam(update, context)
    elif data == "profile_view_career":
        await profile_view_career(update, context)
    elif data == "profile_view_friends":
        await profile_view_friends(update, context)
    elif data == "profile_edit_exam":
        # Redirect to exam handler edit mode
        from mindmate.handlers.exam import _start_edit_mode
        await _start_edit_mode(update, context)
    elif data == "profile_edit_career":
        from mindmate.handlers.career import _start_edit_mode
        await _start_edit_mode(update, context)
    elif data == "profile_edit_friends":
        from mindmate.handlers.friends import friends_show_edit_menu
        await friends_show_edit_menu(update, context)
    elif data == "menu_profile":
        await profile_callback(update, context)
