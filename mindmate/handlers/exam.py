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
    EXAM_TYPE_LABELS_UZ,
    DTM_SUBJECTS,
    DTM_SUBJECT_LABELS_UZ,
    EXAM_LEVELS,
    EXAM_LEVEL_LABELS_UZ,
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
            InlineKeyboardButton("📅 Bugungi rejam", callback_data="exam_plan"),
            InlineKeyboardButton("💬 Savol-javob", callback_data="exam_chat"),
        ],
        [
            InlineKeyboardButton("🧪 Test mashqi", callback_data="exam_practice"),
            InlineKeyboardButton("💪 Stress yengish", callback_data="exam_stress"),
        ],
        [
            InlineKeyboardButton("📊 Mening profilim", callback_data="exam_profile"),
            InlineKeyboardButton("⚙️ Sozlash", callback_data="exam_setup"),
        ],
        [InlineKeyboardButton(t("buttons.back", lang), callback_data="menu_main")],
    ])


def kb_exam_type_select() -> InlineKeyboardMarkup:
    """Exam type selection."""
    rows = []
    for et in EXAM_TYPES:
        rows.append([InlineKeyboardButton(
            EXAM_TYPE_LABELS_UZ.get(et, et),
            callback_data=f"exam_t_{et}",
        )])
    return InlineKeyboardMarkup(rows)


def kb_dtm_subjects(selected: list[str]) -> InlineKeyboardMarkup:
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
    rows.append([InlineKeyboardButton("✅ Tasdiqlash", callback_data="exam_s_done")])
    return InlineKeyboardMarkup(rows)


def kb_exam_level() -> InlineKeyboardMarkup:
    """Current level selection."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(EXAM_LEVEL_LABELS_UZ[lv], callback_data=f"exam_l_{lv}")]
        for lv in EXAM_LEVELS
    ])


def kb_practice_subjects(profile_subjects: list[str]) -> InlineKeyboardMarkup:
    """Pick a subject to practice from user's profile subjects."""
    rows = []
    for subj in profile_subjects[:8]:
        rows.append([InlineKeyboardButton(
            DTM_SUBJECT_LABELS_UZ.get(subj, subj),
            callback_data=f"exam_pq_{subj}",
        )])
    rows.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="exam_back")])
    return InlineKeyboardMarkup(rows)


# ──────────────────────── Handlers ────────────────────────

async def exam_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Entry point — /exam or menu button."""
    user = update.effective_user
    chat = update.effective_chat
    try:
        lang = await user_service.get_user_language(user.id)
        profile = await get_exam_profile(user.id)

        if not profile or not profile.get("exam_type"):
            # New user — start setup wizard
            await chat.send_message(
                "🎓 *Imtihon Mentorga xush kelibsiz!*\n\n"
                "Men sizga DTM, IELTS yoki magistraturaga puxta tayyorlanishda yordam beraman:\n\n"
                "🎯 Shaxsiy o'qish rejasi\n"
                "📚 Har fan bo'yicha savol-javob\n"
                "🧪 Test mashqlari\n"
                "💪 Stressni boshqarish\n\n"
                "Avval qaysi imtihonga tayyorlanyapsiz?",
                reply_markup=kb_exam_type_select(),
                parse_mode="Markdown",
            )
            context.user_data["exam_setup"] = {"step": "exam_type"}
        else:
            # Returning user — show main menu
            await _show_exam_dashboard(update, context, profile, lang, chat=chat)
    except Exception as e:
        logger.error(f"Error in exam_handler: {e}")
        await chat.send_message("Imtihon Mentor")


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
            days_left = f"\n📅 Imtihongacha: *{delta} kun*"
        elif delta == 0:
            days_left = "\n📅 *Imtihon bugun!* 💪"
        else:
            days_left = "\n📅 Imtihon o'tgan"

    subjects_str = ", ".join(DTM_SUBJECT_LABELS_UZ.get(s, s) for s in subjects[:5])
    if len(subjects) > 5:
        subjects_str += f" +{len(subjects) - 5}"
    if not subjects_str:
        subjects_str = "_kiritilmagan_"

    text = (
        f"🎓 *Imtihon Mentor*\n\n"
        f"📌 Imtihon: {EXAM_TYPE_LABELS_UZ.get(exam_type, exam_type)}\n"
        f"📚 Fanlar: {subjects_str}"
        f"{days_left}\n"
        f"🎯 Daraja: {EXAM_LEVEL_LABELS_UZ.get(profile.get('current_level', 'intermediate'), '–')}\n\n"
        f"Bugun nima qilamiz?"
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
                    "📚 *DTM tayyorgarligi*\n\n"
                    "Qaysi fanlarni topshiryapsiz?\n"
                    "Bir nechta tanlang, tugagach *Tasdiqlash* ni bosing.",
                    reply_markup=kb_dtm_subjects([]),
                    parse_mode="Markdown",
                )
            else:
                # For non-DTM, skip subject selection
                context.user_data["exam_setup"]["subjects"] = [exam_type]
                context.user_data["exam_setup"]["step"] = "level"
                await query.edit_message_text(
                    f"✅ *{EXAM_TYPE_LABELS_UZ.get(exam_type)}*\n\n"
                    "Hozirgi darajangiz qanday?",
                    reply_markup=kb_exam_level(),
                    parse_mode="Markdown",
                )
            return

        if data.startswith("exam_s_"):
            tag = data.replace("exam_s_", "")
            setup = context.user_data.get("exam_setup", {})
            subjects = setup.get("subjects", [])

            if tag == "done":
                if not subjects:
                    await query.answer("Kamida 1 ta fan tanlang!", show_alert=True)
                    return
                setup["step"] = "level"
                context.user_data["exam_setup"] = setup
                await query.edit_message_text(
                    "🎯 Hozirgi darajangiz qanday?\n\n"
                    "🌱 Boshlovchi — endi boshlayapman\n"
                    "🌿 O'rta — bazasi bor, mustahkamlash kerak\n"
                    "🌳 Yuqori — deyarli tayyorman, mukammallikka intilaman",
                    reply_markup=kb_exam_level(),
                )
                return

            # Toggle subject
            if tag in subjects:
                subjects.remove(tag)
            else:
                subjects.append(tag)
            setup["subjects"] = subjects
            context.user_data["exam_setup"] = setup
            await query.edit_message_reply_markup(reply_markup=kb_dtm_subjects(subjects))
            return

        if data.startswith("exam_l_"):
            level = data.replace("exam_l_", "")
            setup = context.user_data.get("exam_setup", {})
            setup["level"] = level
            setup["step"] = "exam_date"
            context.user_data["exam_setup"] = setup
            await query.edit_message_text(
                "📅 *Imtihon sanasi*\n\n"
                "Imtihon qachon bo'lishini bilasizmi?\n\n"
                "Sanani quyidagicha yozing: `2026-06-15`\n"
                "(Yil-Oy-Kun formati)\n\n"
                "Yoki bilmasangiz `keyin` deb yozing.",
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
            await query.edit_message_text("⏳ Bugungi rejangizni tuzayapman...")
            try:
                plan = await _engine.generate_daily_plan(profile, lang)
                await query.edit_message_text(
                    plan,
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("⬅️ Orqaga", callback_data="exam_back"),
                    ]]),
                    parse_mode="Markdown",
                )
            except Exception as e:
                logger.error(f"Plan generation error: {e}")
                await query.edit_message_text(
                    "Reja tuzilmadi. Qaytadan urinib ko'ring.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("⬅️ Orqaga", callback_data="exam_back"),
                    ]]),
                )
            return

        if data == "exam_chat":
            context.user_data["mode"] = "exam"
            await query.edit_message_text(
                "💬 *Savol-javob rejimi*\n\n"
                "Endi har qanday savolingizni yozing — fanlar bo'yicha, "
                "vaqt boshqaruvi yoki imtihon strategiyasi haqida.\n\n"
                "Misollar:\n"
                "• Trigonometriyada cosx ning hosilasi nima?\n"
                "• 3 hafta ichida 10 ta mavzuga qanday tayyorgarlik ko'raman?\n"
                "• Imtihondan oldin tunda nima qilish kerak?\n\n"
                "Chiqish uchun /menu",
                reply_markup=get_back_to_menu_keyboard(lang),
                parse_mode="Markdown",
            )
            return

        if data == "exam_practice":
            subjects = profile.get("subjects") or []
            if not subjects:
                await query.edit_message_text(
                    "Avval profilni sozlang — fanlar tanlang.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("⚙️ Sozlash", callback_data="exam_setup"),
                    ]]),
                )
                return
            await query.edit_message_text(
                "🧪 *Test mashqi*\n\nQaysi fan bo'yicha savol kerak?",
                reply_markup=kb_practice_subjects(subjects),
                parse_mode="Markdown",
            )
            return

        if data.startswith("exam_pq_"):
            subject = data.replace("exam_pq_", "")
            await query.edit_message_text("⏳ Savol tuzayapman...")
            try:
                question = await _engine.generate_practice_question(profile, subject, lang)
                context.user_data["last_practice_question"] = question
                context.user_data["mode"] = "exam"
                await query.edit_message_text(
                    question + "\n\n💡 Javobingizni yozing — men baholayman.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("⬅️ Orqaga", callback_data="exam_back"),
                    ]]),
                    parse_mode="Markdown",
                )
            except Exception as e:
                logger.error(f"Practice question error: {e}")
                await query.edit_message_text(
                    "Savol tuzib bo'lmadi. Qaytadan urinib ko'ring.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("⬅️ Orqaga", callback_data="exam_back"),
                    ]]),
                )
            return

        if data == "exam_stress":
            context.user_data["mode"] = "exam"
            await query.edit_message_text(
                "💪 *Stressni boshqarish*\n\n"
                "Imtihon yaqinlashganda nimani his qilyapsiz? Yozing — yordam beraman.\n\n"
                "Misol:\n"
                "• \"Hech narsa esimdan chiqyapti\"\n"
                "• \"Vaqt yetmaydi deb qo'rqaman\"\n"
                "• \"Ota-onam ko'p bosim qilyapti\"",
                reply_markup=get_back_to_menu_keyboard(lang),
                parse_mode="Markdown",
            )
            return

        if data == "exam_profile":
            await _show_exam_dashboard(update, context, profile, lang, edit_query=query)
            return

        if data == "exam_setup":
            await query.edit_message_text(
                "⚙️ *Profilni qayta sozlash*\n\n"
                "Bu eski profilni o'chirib, yangi sozlashni boshlaydi. Davom etamizmi?",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ Ha, qaytadan", callback_data="exam_reset_yes")],
                    [InlineKeyboardButton("❌ Bekor qilish", callback_data="exam_back")],
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
            await query.edit_message_text("Xatolik yuz berdi.")
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

    # ── Wizard: exam_date step ─────────────────────────────────────
    if setup and setup.get("step") == "exam_date":
        exam_date = None
        if text.lower() not in ("keyin", "later", "skip", "пропустить"):
            try:
                exam_date = datetime.strptime(text, "%Y-%m-%d").date()
                if exam_date < date.today():
                    await message.reply_text(
                        "❌ Sana o'tgan kun. Iltimos, kelajakdagi sanani kiriting (`2026-06-15` shaklida)."
                    )
                    return
            except ValueError:
                await message.reply_text(
                    "❌ Sana noto'g'ri formatda. Misol: `2026-06-15`\n\n"
                    "Yoki `keyin` deb yozing.",
                    parse_mode="Markdown",
                )
                return

        # Save profile
        await upsert_exam_profile(
            user_id=user.id,
            exam_type=setup["exam_type"],
            subjects=setup.get("subjects", []),
            exam_date=exam_date,
            current_level=setup.get("level", "intermediate"),
        )
        context.user_data.pop("exam_setup", None)
        lang = await user_service.get_user_language(user.id)
        profile = await get_exam_profile(user.id)
        await message.reply_text(
            "✅ *Profilingiz tayyor!*\n\n"
            "Endi men sizning shaxsiy mentoringizman. Keling boshlaymiz!",
            parse_mode="Markdown",
        )
        await _show_exam_dashboard(update, context, profile, lang, chat=update.effective_chat)
        return

    # ── Chat mode ──────────────────────────────────────────────────
    if context.user_data.get("mode") != "exam":
        return  # Not for us

    profile = await get_exam_profile(user.id)
    if not profile:
        await message.reply_text("Avval imtihon profilini sozlang. /exam")
        return

    lang = await user_service.get_user_language(user.id)

    # Free-tier limit
    if not await is_premium_active(user.id):
        usage = await get_daily_usage(user.id)
        if usage["ai_messages"] >= FREE_DAILY_AI_MESSAGES:
            await message.reply_text(
                t("premium.limit_reached", lang).format(limit=FREE_DAILY_AI_MESSAGES),
                reply_markup=get_back_to_menu_keyboard(lang),
            )
            return

    # Chat with the exam engine
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
        await message.reply_text("Texnik xatolik. Qaytadan urinib ko'ring.")
