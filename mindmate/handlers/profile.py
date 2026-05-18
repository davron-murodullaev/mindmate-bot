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
from mindmate.core.constants import DTM_SUBJECT_LABELS_UZ

logger = logging.getLogger(__name__)


def _profile_keyboard(lang: str, has_exam: bool, has_career: bool, has_friends: bool) -> InlineKeyboardMarkup:
    """Build profile keyboard with edit buttons for each configured section."""
    rows = []

    if has_exam:
        rows.append([
            InlineKeyboardButton(t("profile.exam_view_btn", lang), callback_data="profile_view_exam"),
            InlineKeyboardButton(t("profile.edit_btn", lang), callback_data="profile_edit_exam"),
        ])
    else:
        rows.append([InlineKeyboardButton(t("profile.exam_setup_btn", lang), callback_data="menu_exam")])

    if has_career:
        rows.append([
            InlineKeyboardButton(t("profile.career_view_btn", lang), callback_data="profile_view_career"),
            InlineKeyboardButton(t("profile.edit_btn", lang), callback_data="profile_edit_career"),
        ])
    else:
        rows.append([InlineKeyboardButton(t("profile.career_setup_btn", lang), callback_data="menu_career")])

    if has_friends:
        rows.append([
            InlineKeyboardButton(t("profile.friends_view_btn", lang), callback_data="profile_view_friends"),
            InlineKeyboardButton(t("profile.edit_btn", lang), callback_data="profile_edit_friends"),
        ])
    else:
        rows.append([InlineKeyboardButton(t("profile.friends_setup_btn", lang), callback_data="menu_friends")])

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

    name = first_name or t("menu.friends", lang)
    badge = t("profile.badge_premium", lang) if is_pro else t("profile.badge_free", lang)
    no_entry = t("profile.no_entry", lang)

    title_tpl = t("profile.title", lang)
    lines = [f"👤 *{title_tpl.format(name=name)}* — {badge}\n"]

    # Exam section
    if exam and exam.get("exam_type"):
        exam_type = t(f"exam.type.{exam['exam_type']}", lang)
        level_key = exam.get("current_level", "")
        level = t(f"exam.level.{level_key}", lang) if level_key else "–"
        subjects = exam.get("subjects") or []
        subj_str = ", ".join(DTM_SUBJECT_LABELS_UZ.get(s, s) for s in subjects[:3])
        if len(subjects) > 3:
            subj_str += f" +{len(subjects)-3}"
        lines.append(f"🎓 *{t('menu.exam', lang)}:* {exam_type} · {level}")
        if subj_str:
            lines.append(f"   {subj_str}")
        if exam.get("exam_date"):
            from datetime import date
            delta = (exam["exam_date"] - date.today()).days
            if delta > 0:
                days_left = t("profile.days_left", lang).format(delta=delta)
                lines.append(f"   📅 {exam['exam_date']} ({days_left})")
            else:
                lines.append(f"   📅 {exam['exam_date']}")

    # Career section
    if career and career.get("status"):
        status = t(f"career.status.{career['status']}", lang)
        role = career.get("target_role") or "–"
        lines.append(f"💼 *{t('menu.career', lang)}:* {status}")
        if career.get("target_role"):
            lines.append(f"   {t('profile.career_detail.role', lang)}: {role}")

    # Friends section
    if friends and friends.get("display_name"):
        from mindmate.core.constants import FRIEND_LOOKING_OPTIONS
        lf_key = friends.get("looking_for", "")
        looking = t(f"friends.looking_for.{lf_key}", lang) if lf_key in FRIEND_LOOKING_OPTIONS else "–"
        verified_str = t("profile.verified", lang) if friends.get("is_verified") else t("profile.pending_verify", lang)
        lines.append(f"💝 *{t('menu.friends', lang)}:* {friends['display_name']} · {verified_str}")
        lines.append(f"   {t('profile.friends_detail.goal', lang)}: {looking}")

    if len(lines) == 2:
        lines.append(t("profile.empty_hint", lang))

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
            await query.answer(t("profile.exam_not_found", lang), show_alert=True)
            return

        from datetime import date
        exam_type = t(f"exam.type.{exam.get('exam_type', '')}", lang)
        level_key = exam.get("current_level", "")
        level = t(f"exam.level.{level_key}", lang) if level_key else "–"
        subjects = exam.get("subjects") or []
        no_entry = t("profile.no_entry", lang)
        subj_str = "\n   ".join(f"• {DTM_SUBJECT_LABELS_UZ.get(s, s)}" for s in subjects) or no_entry
        exam_date = exam.get("exam_date")
        if exam_date:
            delta = (exam_date - date.today()).days
            if delta > 0:
                days_left = t("profile.days_left", lang).format(delta=delta)
                date_str = f"{exam_date} ({days_left})"
            else:
                date_str = f"{exam_date} ({t('profile.exam_passed', lang)})"
        else:
            date_str = no_entry
        hours = exam.get("daily_study_hours", 4)

        d = "profile.exam_detail"
        text = (
            f"{t(f'{d}.title', lang)}\n\n"
            f"{t(f'{d}.exam_type', lang)}: {exam_type}\n"
            f"{t(f'{d}.level', lang)}: {level}\n"
            f"{t(f'{d}.subjects', lang)}:\n   {subj_str}\n"
            f"{t(f'{d}.date', lang)}: {date_str}\n"
            f"{t(f'{d}.daily_hours', lang).format(hours=hours)}"
        )
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(t("profile.edit_btn", lang), callback_data="profile_edit_exam")],
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
            await query.answer(t("profile.career_not_found", lang), show_alert=True)
            return

        no_entry = t("profile.no_entry", lang)
        status = t(f"career.status.{career.get('status', '')}", lang)
        role = career.get("target_role") or no_entry
        industry = career.get("industry") or no_entry
        exp = career.get("experience_years", 0)
        skills = career.get("skills") or []
        skills_str = ", ".join(skills[:5]) if skills else no_entry

        d = "profile.career_detail"
        text = (
            f"{t(f'{d}.title', lang)}\n\n"
            f"{t(f'{d}.status', lang)}: {status}\n"
            f"{t(f'{d}.role', lang)}: {role}\n"
            f"{t(f'{d}.industry', lang)}: {industry}\n"
            f"{t(f'{d}.experience', lang).format(exp=exp)}\n"
            f"{t(f'{d}.skills', lang)}: {skills_str}"
        )
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(t("profile.edit_btn", lang), callback_data="profile_edit_career")],
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
            await query.answer(t("profile.friends_not_found", lang), show_alert=True)
            return

        from mindmate.core.constants import (
            FRIEND_LOOKING_OPTIONS,
            FRIEND_GENDER_OPTIONS,
            FRIEND_INTERESTS as _FRIEND_INTERESTS,
        )
        no_entry = t("profile.no_entry", lang)
        name = friends.get("display_name", "–")
        age = friends.get("age", "–")
        gender_key = friends.get("gender", "")
        gender = t(f"friends.gender.{gender_key}", lang) if gender_key in FRIEND_GENDER_OPTIONS else "–"
        city = friends.get("city") or no_entry
        lf_key = friends.get("looking_for", "")
        looking = t(f"friends.looking_for.{lf_key}", lang) if lf_key in FRIEND_LOOKING_OPTIONS else "–"
        interests = friends.get("interests") or []
        interests_str = ", ".join(
            t(f"friends.interests.{i}", lang) if i in _FRIEND_INTERESTS else i
            for i in interests[:5]
        )
        bio = friends.get("bio") or no_entry
        verified = t("profile.verified", lang) if friends.get("is_verified") else t("profile.pending_verify", lang)
        active = t("profile.visible", lang) if friends.get("is_active") else t("profile.hidden", lang)

        d = "profile.friends_detail"
        text = (
            f"{t(f'{d}.title', lang)}\n\n"
            f"{t(f'{d}.name', lang)}: {name}\n"
            f"{t(f'{d}.age', lang)}: {age}\n"
            f"{t(f'{d}.gender', lang)}: {gender}\n"
            f"{t(f'{d}.city', lang)}: {city}\n"
            f"{t(f'{d}.goal', lang)}: {looking}\n"
            f"{t(f'{d}.interests', lang)}: {interests_str or no_entry}\n"
            f"{t(f'{d}.bio', lang)}: _{bio}_\n"
            f"{t(f'{d}.status', lang)}: {verified} · {active}"
        )
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(t("profile.edit_btn", lang), callback_data="profile_edit_friends")],
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
