"""
Career coach handler — resume builder, interview prep, salary negotiation.

Flow:
1. /career or "💼 Karyera" button
2. If no profile → setup wizard (status, target role, experience)
3. Otherwise → career menu (resume, interview, advice, etc.)
"""
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from mindmate.services.user_service import user_service
from mindmate.db.queries import (
    get_career_profile,
    upsert_career_profile,
    delete_career_profile,
    increment_ai_usage,
    get_daily_usage,
    is_premium_active,
)
from mindmate.ai.memory import ConversationMemory
from mindmate.ai.engines.career_engine import CareerEngine
from mindmate.ai.formatter import format_response
from mindmate.ui.keyboards import get_back_to_menu_keyboard
from mindmate.i18n import t
from mindmate.core.constants import (
    CAREER_STATUS_OPTIONS,
    FREE_DAILY_AI_MESSAGES,
)

logger = logging.getLogger(__name__)

_memory = ConversationMemory()
_engine = CareerEngine()


# ──────────────────────── Keyboards ────────────────────────

def kb_career_main(lang: str = "uz") -> InlineKeyboardMarkup:
    """Main career coach menu."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(t("career.menu.resume", lang), callback_data="career_resume"),
            InlineKeyboardButton(t("career.menu.review", lang), callback_data="career_review"),
        ],
        [
            InlineKeyboardButton(t("career.menu.interview", lang), callback_data="career_interview"),
            InlineKeyboardButton(t("career.menu.chat", lang), callback_data="career_chat"),
        ],
        [
            InlineKeyboardButton(t("career.menu.salary", lang), callback_data="career_salary"),
            InlineKeyboardButton(t("career.menu.plan", lang), callback_data="career_plan"),
        ],
        [
            InlineKeyboardButton(t("career.menu.my_profile", lang), callback_data="career_setup"),
            InlineKeyboardButton(t("buttons.back", lang), callback_data="menu_main"),
        ],
    ])


def kb_career_status(lang: str = "uz") -> InlineKeyboardMarkup:
    """Career status selection."""
    rows = [
        [InlineKeyboardButton(t(f"career.status.{s}", lang), callback_data=f"career_st_{s}")]
        for s in CAREER_STATUS_OPTIONS
    ]
    rows.append([InlineKeyboardButton(t("buttons.cancel", lang), callback_data="career_wizard_cancel")])
    return InlineKeyboardMarkup(rows)


def kb_career_cancel(lang: str = "uz") -> InlineKeyboardMarkup:
    """Cancel keyboard for text-input steps in the career wizard."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("buttons.cancel", lang), callback_data="career_wizard_cancel")],
    ])


def kb_interview_type(lang: str = "uz") -> InlineKeyboardMarkup:
    """Interview question type selection."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("career.interview.general", lang), callback_data="career_iq_general")],
        [InlineKeyboardButton(t("career.interview.technical", lang), callback_data="career_iq_technical")],
        [InlineKeyboardButton(t("career.interview.behavioral", lang), callback_data="career_iq_behavioral")],
        [InlineKeyboardButton(t("buttons.back", lang), callback_data="career_back")],
    ])


def kb_career_status_edit(lang: str = "uz") -> InlineKeyboardMarkup:
    """Status selection for edit mode."""
    rows = [
        [InlineKeyboardButton(t(f"career.status.{s}", lang), callback_data=f"career_est_{s}")]
        for s in CAREER_STATUS_OPTIONS
    ]
    rows.append([InlineKeyboardButton(t("buttons.back", lang), callback_data="career_edit_back")])
    return InlineKeyboardMarkup(rows)


def kb_career_edit_menu(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("career.edit.field_status", lang), callback_data="career_edit_status")],
        [InlineKeyboardButton(t("career.edit.field_role", lang), callback_data="career_edit_role")],
        [InlineKeyboardButton(t("career.edit.field_experience", lang), callback_data="career_edit_experience")],
        [InlineKeyboardButton(t("buttons.back", lang), callback_data="menu_profile")],
    ])


# ──────────────────────── Handlers ────────────────────────

async def _start_edit_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show career profile with per-field edit buttons (non-destructive)."""
    query = update.callback_query
    user = query.from_user
    try:
        try:
            await query.answer()
        except Exception:
            pass
        lang = await user_service.get_user_language(user.id)
        profile = await get_career_profile(user.id)
        if not profile or not profile.get("status"):
            context.user_data["career_setup"] = {"step": "status"}
            await query.edit_message_text(
                t("career.select_status", lang),
                reply_markup=kb_career_status(lang),
                parse_mode="Markdown",
            )
            return

        status = t(f"career.status.{profile.get('status', '')}", lang)
        role = profile.get("target_role") or t("profile.no_entry", lang)
        exp = profile.get("experience_years", 0)

        text = (
            f"{t('career.edit.title', lang)}\n\n"
            f"{t('career.edit.field_status', lang)}: {status}\n"
            f"{t('career.edit.field_role', lang)}: {role}\n"
            f"{t('career.edit.field_experience', lang)}: {exp}\n\n"
            f"{t('career.edit.what_to_change', lang)}"
        )
        await query.edit_message_text(text, reply_markup=kb_career_edit_menu(lang), parse_mode="Markdown")
    except Exception as e:
        logger.error(f"career _start_edit_mode error: {e}")


async def career_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Entry point — /career command or menu button.

    For NEW users: show teaser with [Boshlash] / [Orqaga] buttons.
    Wizard only starts when user explicitly opts in.
    """
    user = update.effective_user
    chat = update.effective_chat
    try:
        lang = await user_service.get_user_language(user.id)
        profile = await get_career_profile(user.id)

        if not profile or not profile.get("status"):
            await chat.send_message(
                t("career.teaser", lang),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(t("career.start_btn", lang), callback_data="career_start_setup")],
                    [InlineKeyboardButton(t("buttons.back", lang), callback_data="menu_main")],
                ]),
                parse_mode="Markdown",
            )
        else:
            await _show_career_dashboard(update, context, profile, lang, chat=chat)
    except Exception as e:
        logger.error(f"Error in career_handler: {e}")
        await chat.send_message(t("errors.generic", "en"))


async def _show_career_dashboard(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    profile: dict,
    lang: str,
    chat=None,
    edit_query=None,
) -> None:
    """Render the career dashboard with profile summary."""
    status_key = profile.get("status", "")
    status = t(f"career.status.{status_key}", lang) if status_key else "–"
    target = profile.get("target_role") or f"_{t('profile.no_entry', lang)}_"
    industry = profile.get("industry") or f"_{t('profile.no_entry', lang)}_"
    exp = profile.get("experience_years", 0)

    no_entry = t("profile.no_entry", lang)
    exp_label = t("profile.career_detail.experience", lang).format(exp=exp)

    text = (
        f"{t('career.dashboard_title', lang)}\n\n"
        f"{t('profile.career_detail.status', lang)}: {status}\n"
        f"{t('profile.career_detail.role', lang)}: {target}\n"
        f"{t('profile.career_detail.industry', lang)}: {industry}\n"
        f"{exp_label}\n\n"
        f"{t('career.dashboard_prompt', lang)}"
    )

    kb = kb_career_main(lang)
    if edit_query:
        try:
            await edit_query.edit_message_text(text, reply_markup=kb, parse_mode="Markdown")
            return
        except Exception:
            pass
    if chat:
        await chat.send_message(text, reply_markup=kb, parse_mode="Markdown")


async def career_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle all career_* callbacks."""
    query = update.callback_query
    user = query.from_user
    try:
        await query.answer()
        lang = await user_service.get_user_language(user.id)
        data = query.data or ""

        # ── Start wizard (opt-in from teaser) ─────────────────────
        if data == "career_start_setup":
            context.user_data["career_setup"] = {"step": "status"}
            await query.edit_message_text(
                t("career.select_status", lang),
                reply_markup=kb_career_status(lang),
                parse_mode="Markdown",
            )
            return

        if data == "career_wizard_cancel":
            context.user_data.pop("career_setup", None)
            context.user_data.pop("career_edit", None)
            context.user_data.pop("career_action", None)
            existing = await get_career_profile(user.id)
            if existing and existing.get("status"):
                await _show_career_dashboard(update, context, existing, lang, edit_query=query)
            else:
                try:
                    await query.delete_message()
                except Exception:
                    pass
                await career_handler(update, context)
            return

        # ── Per-field edit mode ────────────────────────────────────
        if data == "career_edit_back":
            await _start_edit_mode(update, context)
            return

        if data == "career_edit_status":
            await query.edit_message_text(
                t("career.edit.change_status", lang),
                reply_markup=kb_career_status_edit(lang),
                parse_mode="Markdown",
            )
            return

        if data.startswith("career_est_"):
            new_status = data.replace("career_est_", "")
            existing = await get_career_profile(user.id)
            if existing:
                await upsert_career_profile(
                    user_id=user.id,
                    status=new_status,
                    target_role=existing.get("target_role"),
                    experience_years=existing.get("experience_years", 0),
                )
            await _start_edit_mode(update, context)
            return

        if data == "career_edit_role":
            context.user_data["career_edit"] = {"field": "role"}
            await query.edit_message_text(
                t("career.edit.enter_role", lang),
                parse_mode="Markdown",
            )
            return

        if data == "career_edit_experience":
            context.user_data["career_edit"] = {"field": "experience"}
            await query.edit_message_text(
                t("career.edit.enter_experience", lang),
                parse_mode="Markdown",
            )
            return

        # ── Setup wizard ───────────────────────────────────────────
        if data.startswith("career_st_"):
            status = data.replace("career_st_", "")
            context.user_data["career_setup"] = {
                "step": "target_role",
                "status": status,
            }
            await query.edit_message_text(
                t("career.enter_role", lang),
                reply_markup=kb_career_cancel(lang),
                parse_mode="Markdown",
            )
            return

        # ── Dashboard actions ──────────────────────────────────────
        profile = await get_career_profile(user.id)
        if not profile:
            await career_handler(update, context)
            return

        if data == "career_back":
            await _show_career_dashboard(update, context, profile, lang, edit_query=query)
            return

        if data == "career_resume":
            context.user_data["mode"] = "career"
            context.user_data["career_action"] = "resume"
            await query.edit_message_text(
                t("career.resume_intro", lang),
                reply_markup=get_back_to_menu_keyboard(lang),
                parse_mode="Markdown",
            )
            return

        if data == "career_review":
            context.user_data["mode"] = "career"
            context.user_data["career_action"] = "review"
            await query.edit_message_text(
                t("career.review_intro", lang),
                reply_markup=get_back_to_menu_keyboard(lang),
                parse_mode="Markdown",
            )
            return

        if data == "career_interview":
            await query.edit_message_text(
                t("career.interview.select", lang),
                reply_markup=kb_interview_type(lang),
                parse_mode="Markdown",
            )
            return

        if data.startswith("career_iq_"):
            qtype = data.replace("career_iq_", "")
            await query.edit_message_text(t("career.interview.loading", lang))
            try:
                question = await _engine.generate_interview_question(profile, qtype, lang)
                context.user_data["interview_question"] = question
                context.user_data["mode"] = "career"
                context.user_data["career_action"] = "interview_answer"
                await query.edit_message_text(
                    f"{question}\n\n"
                    f"{t('career.interview.answer_prompt', lang)}",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton(t("buttons.back", lang), callback_data="career_back"),
                    ]]),
                    parse_mode="Markdown",
                )
            except Exception as e:
                logger.error(f"Interview question error: {e}")
                await query.edit_message_text(
                    t("career.interview.error", lang),
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton(t("buttons.back", lang), callback_data="career_back"),
                    ]]),
                )
            return

        if data == "career_chat":
            context.user_data["mode"] = "career"
            context.user_data["career_action"] = "chat"
            await query.edit_message_text(
                t("career.chat_intro", lang),
                reply_markup=get_back_to_menu_keyboard(lang),
                parse_mode="Markdown",
            )
            return

        if data == "career_salary":
            context.user_data["mode"] = "career"
            context.user_data["career_action"] = "chat"
            await query.edit_message_text(
                t("career.salary_intro", lang),
                reply_markup=get_back_to_menu_keyboard(lang),
                parse_mode="Markdown",
            )
            return

        if data == "career_plan":
            context.user_data["mode"] = "career"
            context.user_data["career_action"] = "chat"
            await query.edit_message_text(
                t("career.plan_intro", lang),
                reply_markup=get_back_to_menu_keyboard(lang),
                parse_mode="Markdown",
            )
            return

        if data == "career_setup":
            await query.edit_message_text(
                t("career.reset_confirm", lang),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(t("career.reset_yes", lang), callback_data="career_reset_yes")],
                    [InlineKeyboardButton(t("career.reset_cancel", lang), callback_data="career_back")],
                ]),
                parse_mode="Markdown",
            )
            return

        if data == "career_reset_yes":
            await delete_career_profile(user.id)
            context.user_data.pop("career_setup", None)
            await career_handler(update, context)
            return

    except Exception as e:
        logger.error(f"Error in career_callback: {e}")
        try:
            await query.edit_message_text(t("errors.generic", "en"))
        except Exception:
            pass


async def career_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages during career mode (setup wizard or actions)."""
    user = update.effective_user
    message = update.message
    if not message or not message.text:
        return

    setup = context.user_data.get("career_setup")
    text = message.text.strip()

    lang = await user_service.get_user_language(user.id)

    # ── Edit mode: individual field text input ─────────────────────
    career_edit = context.user_data.get("career_edit", {})
    if career_edit.get("field") == "role":
        profile = await get_career_profile(user.id)
        if profile:
            await upsert_career_profile(
                user_id=user.id,
                status=profile["status"],
                target_role=text,
                experience_years=profile.get("experience_years", 0),
            )
        context.user_data.pop("career_edit", None)
        await message.reply_text(t("career.edit.role_updated", lang))
        profile = await get_career_profile(user.id)
        await _show_career_dashboard(update, context, profile, lang, chat=update.effective_chat)
        return

    if career_edit.get("field") == "experience":
        try:
            exp = int(text)
            if exp < 0 or exp > 60:
                raise ValueError
        except ValueError:
            await message.reply_text(t("career.exp_invalid", lang))
            return
        profile = await get_career_profile(user.id)
        if profile:
            await upsert_career_profile(
                user_id=user.id,
                status=profile["status"],
                target_role=profile.get("target_role"),
                experience_years=exp,
            )
        context.user_data.pop("career_edit", None)
        await message.reply_text(t("career.edit.exp_updated", lang))
        profile = await get_career_profile(user.id)
        await _show_career_dashboard(update, context, profile, lang, chat=update.effective_chat)
        return

    # ── Wizard: target_role step ───────────────────────────────────
    if setup and setup.get("step") == "target_role":
        setup["target_role"] = text
        setup["step"] = "experience"
        context.user_data["career_setup"] = setup
        await message.reply_text(
            t("career.enter_exp", lang),
            reply_markup=kb_career_cancel(lang),
            parse_mode="Markdown",
        )
        return

    if setup and setup.get("step") == "experience":
        try:
            exp = int(text)
            if exp < 0 or exp > 60:
                raise ValueError
        except ValueError:
            await message.reply_text(
                t("career.exp_invalid", lang),
                reply_markup=kb_career_cancel(lang),
            )
            return

        await upsert_career_profile(
            user_id=user.id,
            status=setup["status"],
            target_role=setup.get("target_role"),
            experience_years=exp,
        )
        context.user_data.pop("career_setup", None)
        profile = await get_career_profile(user.id)
        await message.reply_text(
            t("career.setup_done", lang),
            parse_mode="Markdown",
        )
        await _show_career_dashboard(update, context, profile, lang, chat=update.effective_chat)
        return

    # ── Career actions ─────────────────────────────────────────────
    if context.user_data.get("mode") != "career":
        return

    profile = await get_career_profile(user.id)
    if not profile:
        await message.reply_text(t("career.no_profile", lang))
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

    action = context.user_data.get("career_action", "chat")

    try:
        await message.chat.send_action("typing")

        if action == "resume":
            await message.reply_text(t("career.resume_loading", lang))
            response = await _engine.generate_resume(profile, text, lang)
            await upsert_career_profile(
                user_id=user.id,
                status=profile["status"],
                target_role=profile.get("target_role"),
                industry=profile.get("industry"),
                experience_years=profile.get("experience_years", 0),
                skills=profile.get("skills"),
                languages=profile.get("languages"),
                resume_text=response,
            )
            await message.reply_text(
                response,
                reply_markup=get_back_to_menu_keyboard(lang),
                parse_mode="Markdown",
            )
            context.user_data.pop("career_action", None)

        elif action == "review":
            await message.reply_text(t("career.review_loading", lang))
            history = await _memory.get_history(user.id, "career")
            await _memory.add_message(user.id, "career", "user", f"My resume:\n{text}\n\nPlease analyze it.")
            response = await _engine.process(
                message=f"My resume:\n{text}\n\nPlease provide a professional analysis: strengths, weaknesses, and specific improvement suggestions.",
                history=history,
                context={"lang": lang, "career_profile": profile},
            )
            await _memory.add_message(user.id, "career", "assistant", response)
            await message.reply_text(
                response,
                reply_markup=get_back_to_menu_keyboard(lang),
            )
            context.user_data.pop("career_action", None)

        elif action == "interview_answer":
            question = context.user_data.get("interview_question", "")
            await message.reply_text(t("career.interview.evaluating", lang))
            response = await _engine.evaluate_interview_answer(profile, question, text, lang)
            await message.reply_text(
                response,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(t("career.interview.another", lang), callback_data="career_interview")],
                    [InlineKeyboardButton(t("buttons.back", lang), callback_data="career_back")],
                ]),
                parse_mode="Markdown",
            )
            context.user_data.pop("career_action", None)
            context.user_data.pop("interview_question", None)

        else:  # chat
            history = await _memory.get_history(user.id, "career")
            await _memory.add_message(user.id, "career", "user", text)
            response = await _engine.process(
                message=text,
                history=history,
                context={"lang": lang, "career_profile": profile},
            )
            await _memory.add_message(user.id, "career", "assistant", response)
            await message.reply_text(format_response(response, mode="career"))

        await increment_ai_usage(user.id)
    except Exception as e:
        logger.error(f"Career action error: {e}")
        await message.reply_text(t("errors.generic", lang))
