"""
Exam mentor handler — DTM/IELTS/SAT/Magistratura with setup wizard.

Flow:
1. /exam or "📚 Imtihon Mentor" button
2. If no profile → setup wizard
3. Otherwise → exam menu (today's plan, Q&A, practice, stress, progress)
"""
import logging
from datetime import date, datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from mindmate.services.user_service import user_service
from mindmate.db.queries import (
    get_exam_profile,
    upsert_exam_profile,
    delete_exam_profile,
    increment_ai_usage,
    get_daily_usage,
    is_premium_active,
)
from mindmate.ai.memory import ConversationMemory
from mindmate.ai.engines.exam_engine import ExamEngine
from mindmate.ai.formatter import format_response
from mindmate.ui.keyboards import get_back_to_menu_keyboard
from mindmate.i18n import t
from mindmate.core.constants import (
    EXAM_TYPES,
    DTM_SUBJECTS,
    DTM_SUBJECT_LABELS_UZ,
    EXAM_LEVELS,
    FREE_DAILY_AI_MESSAGES,
)

logger = logging.getLogger(__name__)

_memory = ConversationMemory()
_engine = ExamEngine()


# ──────────────────────── Keyboards ────────────────────────

def kb_exam_main(lang: str = "uz") -> InlineKeyboardMarkup:
    """Main exam mentor menu (when profile exists)."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(t("exam.menu.plan", lang), callback_data="exam_plan"),
            InlineKeyboardButton(t("exam.menu.chat", lang), callback_data="exam_chat"),
        ],
        [
            InlineKeyboardButton(t("exam.menu.practice", lang), callback_data="exam_practice"),
            InlineKeyboardButton(t("exam.menu.stress", lang), callback_data="exam_stress"),
        ],
        [
            InlineKeyboardButton(t("exam.menu.my_profile", lang), callback_data="exam_profile"),
            InlineKeyboardButton(t("exam.menu.setup", lang), callback_data="exam_setup"),
        ],
        [InlineKeyboardButton(t("buttons.back", lang), callback_data="menu_main")],
    ])


def kb_exam_type_select(lang: str = "uz") -> InlineKeyboardMarkup:
    """Exam type selection."""
    rows = []
    for et in EXAM_TYPES:
        rows.append([InlineKeyboardButton(
            t(f"exam.type.{et}", lang),
            callback_data=f"exam_t_{et}",
        )])
    return InlineKeyboardMarkup(rows)


def kb_dtm_subjects(selected: list[str], lang: str = "uz") -> InlineKeyboardMarkup:
    """Multi-select keyboard for DTM subjects."""
    rows = []
    row = []
    for subj in DTM_SUBJECTS:
        mark = "✅" if subj in selected else ""
        label = DTM_SUBJECT_LABELS_UZ.get(subj, subj)
        row.append(InlineKeyboardButton(
            f"{mark}{label}".strip(),
            callback_data=f"exam_s_{subj}",
        ))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(t("exam.confirm_btn", lang), callback_data="exam_s_done")])
    return InlineKeyboardMarkup(rows)


def kb_exam_level(lang: str = "uz") -> InlineKeyboardMarkup:
    """Current level selection."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t(f"exam.level.{lv}", lang), callback_data=f"exam_l_{lv}")]
        for lv in EXAM_LEVELS
    ])


def kb_practice_subjects(profile_subjects: list[str], lang: str = "uz") -> InlineKeyboardMarkup:
    """Pick a subject to practice from user's profile subjects."""
    rows = []
    for subj in profile_subjects[:8]:
        rows.append([InlineKeyboardButton(
            DTM_SUBJECT_LABELS_UZ.get(subj, subj),
            callback_data=f"exam_pq_{subj}",
        )])
    rows.append([InlineKeyboardButton(t("buttons.back", lang), callback_data="exam_back")])
    return InlineKeyboardMarkup(rows)


def kb_exam_type_edit(lang: str = "uz") -> InlineKeyboardMarkup:
    """Type selection for edit mode — adds back button."""
    rows = [
        [InlineKeyboardButton(t(f"exam.type.{et}", lang), callback_data=f"exam_et_{et}")]
        for et in EXAM_TYPES
    ]
    rows.append([InlineKeyboardButton(t("buttons.back", lang), callback_data="exam_edit_back")])
    return InlineKeyboardMarkup(rows)


def kb_exam_edit_subjects(selected: list[str], lang: str = "uz") -> InlineKeyboardMarkup:
    """Multi-select subject keyboard for edit mode."""
    rows = []
    row = []
    for subj in DTM_SUBJECTS:
        mark = "✅" if subj in selected else ""
        label = DTM_SUBJECT_LABELS_UZ.get(subj, subj)
        row.append(InlineKeyboardButton(f"{mark}{label}".strip(), callback_data=f"exam_es_{subj}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(t("exam.edit.save_btn", lang), callback_data="exam_es_done")])
    rows.append([InlineKeyboardButton(t("buttons.back", lang), callback_data="exam_edit_back")])
    return InlineKeyboardMarkup(rows)


def kb_exam_edit_level(lang: str = "uz") -> InlineKeyboardMarkup:
    """Level selection for edit mode — adds back button."""
    rows = [
        [InlineKeyboardButton(t(f"exam.level.{lv}", lang), callback_data=f"exam_el_{lv}")]
        for lv in EXAM_LEVELS
    ]
    rows.append([InlineKeyboardButton(t("buttons.back", lang), callback_data="exam_edit_back")])
    return InlineKeyboardMarkup(rows)


def kb_exam_edit_menu(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("exam.edit.field_type", lang), callback_data="exam_edit_type")],
        [InlineKeyboardButton(t("exam.edit.field_subjects", lang), callback_data="exam_edit_subjects")],
        [InlineKeyboardButton(t("exam.edit.field_level", lang), callback_data="exam_edit_level")],
        [InlineKeyboardButton(t("exam.edit.field_date", lang), callback_data="exam_edit_date")],
        [InlineKeyboardButton(t("buttons.back", lang), callback_data="menu_profile")],
    ])


# ──────────────────────── Handlers ────────────────────────

async def _start_edit_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show exam profile with per-field edit buttons (non-destructive)."""
    query = update.callback_query
    user = query.from_user
    try:
        try:
            await query.answer()
        except Exception:
            pass
        lang = await user_service.get_user_language(user.id)
        profile = await get_exam_profile(user.id)
        if not profile or not profile.get("exam_type"):
            context.user_data["exam_setup"] = {"step": "exam_type"}
            await query.edit_message_text(
                t("exam.select_type", lang),
                reply_markup=kb_exam_type_select(lang),
                parse_mode="Markdown",
            )
            return

        exam_type = t(f"exam.type.{profile.get('exam_type', '')}", lang)
        level = t(f"exam.level.{profile.get('current_level', 'intermediate')}", lang)
        subjects = profile.get("subjects") or []
        subj_str = ", ".join(DTM_SUBJECT_LABELS_UZ.get(s, s) for s in subjects) or t("profile.no_entry", lang)
        exam_date = profile.get("exam_date")
        date_str = str(exam_date) if exam_date else t("profile.no_entry", lang)

        text = (
            f"{t('exam.edit.title', lang)}\n\n"
            f"{t('profile.exam_detail.exam_type', lang)}: {exam_type}\n"
            f"{t('profile.exam_detail.level', lang)}: {level}\n"
            f"{t('profile.exam_detail.subjects', lang)}: {subj_str}\n"
            f"{t('profile.exam_detail.date', lang)}: {date_str}\n\n"
            f"{t('exam.edit.what_to_change', lang)}"
        )
        await query.edit_message_text(text, reply_markup=kb_exam_edit_menu(lang), parse_mode="Markdown")
    except Exception as e:
        logger.error(f"_start_edit_mode error: {e}")


async def exam_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Entry point — /exam or menu button.

    For NEW users: show teaser with [Boshlash] / [Orqaga] buttons.
    Wizard only starts when user explicitly opts in.
    """
    user = update.effective_user
    chat = update.effective_chat
    try:
        lang = await user_service.get_user_language(user.id)
        profile = await get_exam_profile(user.id)

        if not profile or not profile.get("exam_type"):
            await chat.send_message(
                t("exam.teaser", lang),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(t("exam.start_btn", lang), callback_data="exam_start_setup")],
                    [InlineKeyboardButton(t("buttons.back", lang), callback_data="menu_main")],
                ]),
                parse_mode="Markdown",
            )
        else:
            await _show_exam_dashboard(update, context, profile, lang, chat=chat)
    except Exception as e:
        logger.error(f"Error in exam_handler: {e}")
        await chat.send_message(t("errors.generic", "en"))


async def _show_exam_dashboard(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    profile: dict,
    lang: str,
    chat=None,
    edit_query=None,
) -> None:
    """Render the exam dashboard with profile summary."""
    exam_type = profile.get("exam_type", "dtm")
    subjects = profile.get("subjects") or []
    exam_date = profile.get("exam_date")
    days_left = ""
    if exam_date:
        delta = (exam_date - date.today()).days
        if delta > 0:
            days_left = f"\n📅 {t('profile.days_left', lang, delta=delta)}"
        elif delta == 0:
            days_left = f"\n📅 *{t('profile.exam_today', lang)}*"
        else:
            days_left = f"\n📅 {t('profile.exam_passed', lang)}"

    subjects_str = ", ".join(DTM_SUBJECT_LABELS_UZ.get(s, s) for s in subjects[:5])
    if len(subjects) > 5:
        subjects_str += f" +{len(subjects) - 5}"
    if not subjects_str:
        subjects_str = f"_{t('profile.no_entry', lang)}_"

    level_key = profile.get("current_level", "intermediate")
    text = (
        f"{t('exam.dashboard_title', lang)}\n\n"
        f"{t('profile.exam_detail.exam_type', lang)}: {t(f'exam.type.{exam_type}', lang)}\n"
        f"{t('profile.exam_detail.subjects', lang)}: {subjects_str}"
        f"{days_left}\n"
        f"{t('profile.exam_detail.level', lang)}: {t(f'exam.level.{level_key}', lang)}\n\n"
        f"{t('exam.dashboard_prompt', lang)}"
    )

    kb = kb_exam_main(lang)
    if edit_query:
        try:
            await edit_query.edit_message_text(text, reply_markup=kb, parse_mode="Markdown")
            return
        except Exception:
            pass
    if chat:
        await chat.send_message(text, reply_markup=kb, parse_mode="Markdown")


async def exam_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle all exam_* callbacks."""
    query = update.callback_query
    user = query.from_user
    try:
        await query.answer()
        lang = await user_service.get_user_language(user.id)
        data = query.data or ""

        # ── Start wizard (opt-in from teaser) ─────────────────────
        if data == "exam_start_setup":
            context.user_data["exam_setup"] = {"step": "exam_type"}
            await query.edit_message_text(
                t("exam.select_type", lang),
                reply_markup=kb_exam_type_select(lang),
                parse_mode="Markdown",
            )
            return

        if data == "exam_wizard_cancel":
            context.user_data.pop("exam_setup", None)
            context.user_data.pop("exam_edit", None)
            existing = await get_exam_profile(user.id)
            if existing and existing.get("exam_type"):
                await _show_exam_dashboard(update, context, existing, lang, edit_query=query)
            else:
                try:
                    await query.delete_message()
                except Exception:
                    pass
                await exam_handler(update, context)
            return

        # ── Per-field edit mode ────────────────────────────────────
        if data == "exam_edit_back":
            await _start_edit_mode(update, context)
            return

        if data == "exam_edit_type":
            await query.edit_message_text(
                t("exam.edit.change_type", lang),
                reply_markup=kb_exam_type_edit(lang),
                parse_mode="Markdown",
            )
            return

        if data.startswith("exam_et_"):
            new_type = data.replace("exam_et_", "")
            existing = await get_exam_profile(user.id)
            if existing:
                await upsert_exam_profile(
                    user_id=user.id,
                    exam_type=new_type,
                    subjects=existing.get("subjects") or [],
                    exam_date=existing.get("exam_date"),
                    current_level=existing.get("current_level", "intermediate"),
                )
            await _start_edit_mode(update, context)
            return

        if data == "exam_edit_subjects":
            existing = await get_exam_profile(user.id)
            current_subjects = (existing or {}).get("subjects") or []
            context.user_data["exam_edit"] = {"field": "subjects", "subjects": current_subjects}
            await query.edit_message_text(
                t("exam.edit.change_subjects", lang),
                reply_markup=kb_exam_edit_subjects(current_subjects, lang),
                parse_mode="Markdown",
            )
            return

        if data.startswith("exam_es_"):
            tag = data.replace("exam_es_", "")
            edit = context.user_data.get("exam_edit", {})
            subjects = list(edit.get("subjects", []))

            if tag == "done":
                if not subjects:
                    await query.answer(t("exam.min_subject_warn", lang), show_alert=True)
                    return
                existing = await get_exam_profile(user.id)
                if existing:
                    await upsert_exam_profile(
                        user_id=user.id,
                        exam_type=existing["exam_type"],
                        subjects=subjects,
                        exam_date=existing.get("exam_date"),
                        current_level=existing.get("current_level", "intermediate"),
                    )
                context.user_data.pop("exam_edit", None)
                await _start_edit_mode(update, context)
                return

            if tag in subjects:
                subjects.remove(tag)
            else:
                subjects.append(tag)
            edit["subjects"] = subjects
            context.user_data["exam_edit"] = edit
            await query.edit_message_reply_markup(reply_markup=kb_exam_edit_subjects(subjects, lang))
            return

        if data == "exam_edit_level":
            await query.edit_message_text(
                t("exam.edit.change_level", lang),
                reply_markup=kb_exam_edit_level(lang),
                parse_mode="Markdown",
            )
            return

        if data.startswith("exam_el_"):
            new_level = data.replace("exam_el_", "")
            existing = await get_exam_profile(user.id)
            if existing:
                await upsert_exam_profile(
                    user_id=user.id,
                    exam_type=existing["exam_type"],
                    subjects=existing.get("subjects") or [],
                    exam_date=existing.get("exam_date"),
                    current_level=new_level,
                )
            await _start_edit_mode(update, context)
            return

        if data == "exam_edit_date":
            context.user_data["exam_edit"] = {"field": "date"}
            await query.edit_message_text(
                t("exam.edit.enter_date", lang),
                parse_mode="Markdown",
            )
            return

        # ── Setup wizard ───────────────────────────────────────────
        if data.startswith("exam_t_"):
            exam_type = data.replace("exam_t_", "")
            context.user_data["exam_setup"] = {
                "step": "subjects",
                "exam_type": exam_type,
                "subjects": [],
            }
            if exam_type == "dtm":
                await query.edit_message_text(
                    t("exam.dtm_select_subjects", lang),
                    reply_markup=kb_dtm_subjects([], lang),
                    parse_mode="Markdown",
                )
            else:
                context.user_data["exam_setup"]["subjects"] = [exam_type]
                context.user_data["exam_setup"]["step"] = "level"
                await query.edit_message_text(
                    f"✅ *{t(f'exam.type.{exam_type}', lang)}*\n\n{t('exam.select_level', lang)}",
                    reply_markup=kb_exam_level(lang),
                    parse_mode="Markdown",
                )
            return

        if data.startswith("exam_s_"):
            tag = data.replace("exam_s_", "")
            setup = context.user_data.get("exam_setup", {})
            subjects = setup.get("subjects", [])

            if tag == "done":
                if not subjects:
                    await query.answer(t("exam.min_subject_warn", lang), show_alert=True)
                    return
                setup["step"] = "level"
                context.user_data["exam_setup"] = setup
                await query.edit_message_text(
                    t("exam.select_level", lang),
                    reply_markup=kb_exam_level(lang),
                )
                return

            if tag in subjects:
                subjects.remove(tag)
            else:
                subjects.append(tag)
            setup["subjects"] = subjects
            context.user_data["exam_setup"] = setup
            await query.edit_message_reply_markup(reply_markup=kb_dtm_subjects(subjects, lang))
            return

        if data.startswith("exam_l_"):
            level = data.replace("exam_l_", "")
            setup = context.user_data.get("exam_setup", {})
            setup["level"] = level
            setup["step"] = "exam_date"
            context.user_data["exam_setup"] = setup
            await query.edit_message_text(
                t("exam.date_prompt", lang),
                parse_mode="Markdown",
            )
            return

        # ── Dashboard actions ──────────────────────────────────────
        profile = await get_exam_profile(user.id)
        if not profile:
            await exam_handler(update, context)
            return

        if data == "exam_back":
            await _show_exam_dashboard(update, context, profile, lang, edit_query=query)
            return

        if data == "exam_plan":
            await query.edit_message_text(t("exam.plan_loading", lang))
            try:
                plan = await _engine.generate_daily_plan(profile, lang)
                await query.edit_message_text(
                    plan,
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton(t("buttons.back", lang), callback_data="exam_back"),
                    ]]),
                    parse_mode="Markdown",
                )
            except Exception as e:
                logger.error(f"Plan generation error: {e}")
                await query.edit_message_text(
                    t("exam.plan_error", lang),
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton(t("buttons.back", lang), callback_data="exam_back"),
                    ]]),
                )
            return

        if data == "exam_chat":
            context.user_data["mode"] = "exam"
            await query.edit_message_text(
                t("exam.chat_intro", lang),
                reply_markup=get_back_to_menu_keyboard(lang),
                parse_mode="Markdown",
            )
            return

        if data == "exam_practice":
            subjects = profile.get("subjects") or []
            if not subjects:
                await query.edit_message_text(
                    t("exam.no_subjects_warn", lang),
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton(t("exam.menu.setup", lang), callback_data="exam_setup"),
                    ]]),
                )
                return
            await query.edit_message_text(
                t("exam.practice_select", lang),
                reply_markup=kb_practice_subjects(subjects, lang),
                parse_mode="Markdown",
            )
            return

        if data.startswith("exam_pq_"):
            subject = data.replace("exam_pq_", "")
            await query.edit_message_text(t("exam.question_loading", lang))
            try:
                question = await _engine.generate_practice_question(profile, subject, lang)
                context.user_data["last_practice_question"] = question
                context.user_data["mode"] = "exam"
                await query.edit_message_text(
                    question + f"\n\n{t('exam.question_answer_prompt', lang)}",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton(t("buttons.back", lang), callback_data="exam_back"),
                    ]]),
                    parse_mode="Markdown",
                )
            except Exception as e:
                logger.error(f"Practice question error: {e}")
                await query.edit_message_text(
                    t("exam.question_error", lang),
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton(t("buttons.back", lang), callback_data="exam_back"),
                    ]]),
                )
            return

        if data == "exam_stress":
            context.user_data["mode"] = "exam"
            await query.edit_message_text(
                t("exam.stress_intro", lang),
                reply_markup=get_back_to_menu_keyboard(lang),
                parse_mode="Markdown",
            )
            return

        if data == "exam_profile":
            await _show_exam_dashboard(update, context, profile, lang, edit_query=query)
            return

        if data == "exam_setup":
            await query.edit_message_text(
                t("exam.reset_confirm", lang),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(t("exam.reset_yes", lang), callback_data="exam_reset_yes")],
                    [InlineKeyboardButton(t("exam.reset_cancel", lang), callback_data="exam_back")],
                ]),
                parse_mode="Markdown",
            )
            return

        if data == "exam_reset_yes":
            await delete_exam_profile(user.id)
            context.user_data.pop("exam_setup", None)
            await exam_handler(update, context)
            return

    except Exception as e:
        logger.error(f"Error in exam_callback: {e}")
        try:
            _err_lang = lang if 'lang' in locals() else await user_service.get_user_language(user.id)
            await query.edit_message_text(t("errors.generic", _err_lang))
        except Exception:
            pass


async def exam_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages during exam mode (setup wizard or chat)."""
    user = update.effective_user
    message = update.message
    if not message or not message.text:
        return

    setup = context.user_data.get("exam_setup")
    text = message.text.strip()
    lang = await user_service.get_user_language(user.id)

    # ── Edit mode: date field text input ──────────────────────────
    if context.user_data.get("exam_edit", {}).get("field") == "date":
        profile = await get_exam_profile(user.id)
        if not profile:
            context.user_data.pop("exam_edit", None)
            return
        exam_date = None
        skip_words = ("o'chir", "ochir", "clear", "skip", "keyin", "позже", "убрать")
        if text.lower() not in skip_words:
            try:
                exam_date = datetime.strptime(text, "%Y-%m-%d").date()
                if exam_date < date.today():
                    await message.reply_text(
                        t("exam.edit.date_past_error", lang),
                        parse_mode="Markdown",
                    )
                    return
            except ValueError:
                await message.reply_text(
                    t("exam.edit.date_format_error", lang),
                    parse_mode="Markdown",
                )
                return
        await upsert_exam_profile(
            user_id=user.id,
            exam_type=profile["exam_type"],
            subjects=profile.get("subjects") or [],
            exam_date=exam_date,
            current_level=profile.get("current_level", "intermediate"),
        )
        context.user_data.pop("exam_edit", None)
        await message.reply_text(t("exam.edit.date_updated", lang))
        profile = await get_exam_profile(user.id)
        await _show_exam_dashboard(update, context, profile, lang, chat=update.effective_chat)
        return

    # ── Wizard: exam_date step ─────────────────────────────────────
    if setup and setup.get("step") == "exam_date":
        exam_date = None
        skip_words = ("keyin", "later", "skip", "пропустить", "позже")
        if text.lower() not in skip_words:
            try:
                exam_date = datetime.strptime(text, "%Y-%m-%d").date()
                if exam_date < date.today():
                    await message.reply_text(t("exam.date_past_error", lang))
                    return
            except ValueError:
                await message.reply_text(
                    t("exam.date_format_error", lang),
                    parse_mode="Markdown",
                )
                return

        await upsert_exam_profile(
            user_id=user.id,
            exam_type=setup["exam_type"],
            subjects=setup.get("subjects", []),
            exam_date=exam_date,
            current_level=setup.get("level", "intermediate"),
        )
        context.user_data.pop("exam_setup", None)
        profile = await get_exam_profile(user.id)
        await message.reply_text(t("exam.setup_done", lang), parse_mode="Markdown")
        await _show_exam_dashboard(update, context, profile, lang, chat=update.effective_chat)
        return

    # ── Chat mode ──────────────────────────────────────────────────
    if context.user_data.get("mode") != "exam":
        return

    profile = await get_exam_profile(user.id)
    if not profile:
        await message.reply_text(t("exam.no_profile", lang))
        return

    # Free-tier limit
    if not await is_premium_active(user.id):
        usage = await get_daily_usage(user.id)
        if usage["ai_messages"] >= FREE_DAILY_AI_MESSAGES:
            await message.reply_text(
                t("premium.limit_reached", lang).format(limit=FREE_DAILY_AI_MESSAGES),
                reply_markup=get_back_to_menu_keyboard(lang),
            )
            return

    try:
        history = await _memory.get_history(user.id, "exam")
        await _memory.add_message(user.id, "exam", "user", text)

        response = await _engine.process(
            message=text,
            history=history,
            context={"lang": lang, "exam_profile": profile},
        )

        await _memory.add_message(user.id, "exam", "assistant", response)
        await increment_ai_usage(user.id)

        await message.reply_text(format_response(response, mode="exam"))
    except Exception as e:
        logger.error(f"Exam chat error: {e}")
        await message.reply_text(t("errors.generic", lang))
