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
    CAREER_STATUS_LABELS_UZ,
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
            InlineKeyboardButton("📝 Resume yaratish", callback_data="career_resume"),
            InlineKeyboardButton("🔍 Resume tahlili", callback_data="career_review"),
        ],
        [
            InlineKeyboardButton("🎤 Intervyu mashqi", callback_data="career_interview"),
            InlineKeyboardButton("💬 Maslahat olish", callback_data="career_chat"),
        ],
        [
            InlineKeyboardButton("💰 Maosh muzokarasi", callback_data="career_salary"),
            InlineKeyboardButton("📈 Karyera rejasi", callback_data="career_plan"),
        ],
        [
            InlineKeyboardButton("⚙️ Profilim", callback_data="career_setup"),
            InlineKeyboardButton(t("buttons.back", lang), callback_data="menu_main"),
        ],
    ])


def kb_career_status() -> InlineKeyboardMarkup:
    """Career status selection."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(CAREER_STATUS_LABELS_UZ[s], callback_data=f"career_st_{s}")]
        for s in CAREER_STATUS_OPTIONS
    ])


def kb_interview_type() -> InlineKeyboardMarkup:
    """Interview question type selection."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👋 Umumiy savol (HR)", callback_data="career_iq_general")],
        [InlineKeyboardButton("🛠 Texnik savol", callback_data="career_iq_technical")],
        [InlineKeyboardButton("⭐ Behavioral (STAR)", callback_data="career_iq_behavioral")],
        [InlineKeyboardButton("⬅️ Orqaga", callback_data="career_back")],
    ])


# ──────────────────────── Handlers ────────────────────────

async def career_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Entry point — /career command or menu button."""
    user = update.effective_user
    chat = update.effective_chat
    try:
        lang = await user_service.get_user_language(user.id)
        profile = await get_career_profile(user.id)

        if not profile or not profile.get("status"):
            await chat.send_message(
                "💼 *Karyera Coach'ga xush kelibsiz!*\n\n"
                "Men sizga yaxshi ish topish va karyerada o'sishda yordam beraman:\n\n"
                "📝 ATS-friendly resume yaratish\n"
                "🎤 Intervyuga tayyorgarlik\n"
                "💰 Maoshni qanday so'rashni o'rganish\n"
                "📈 6 oylik karyera rejasi\n\n"
                "Boshlash uchun — *hozirgi holatingizni tanlang:*",
                reply_markup=kb_career_status(),
                parse_mode="Markdown",
            )
            context.user_data["career_setup"] = {"step": "status"}
        else:
            await _show_career_dashboard(update, context, profile, lang, chat=chat)
    except Exception as e:
        logger.error(f"Error in career_handler: {e}")
        await chat.send_message("Karyera Coach")


async def _show_career_dashboard(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    profile: dict,
    lang: str,
    chat=None,
    edit_query=None,
) -> None:
    """Render the career dashboard with profile summary."""
    status = profile.get("status", "")
    target = profile.get("target_role") or "_kiritilmagan_"
    industry = profile.get("industry") or "_kiritilmagan_"
    exp = profile.get("experience_years", 0)

    text = (
        f"💼 *Karyera Coach*\n\n"
        f"📌 Holat: {CAREER_STATUS_LABELS_UZ.get(status, status)}\n"
        f"🎯 Maqsad: {target}\n"
        f"🏢 Soha: {industry}\n"
        f"⏱ Tajriba: {exp} yil\n\n"
        f"Bugun nima qilamiz?"
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

        # ── Setup wizard ───────────────────────────────────────────
        if data.startswith("career_st_"):
            status = data.replace("career_st_", "")
            context.user_data["career_setup"] = {
                "step": "target_role",
                "status": status,
            }
            await query.edit_message_text(
                "🎯 *Maqsad lavozim*\n\n"
                "Qaysi lavozimda ishlamoqchisiz?\n\n"
                "Misollar:\n"
                "• Frontend Developer\n"
                "• HR Manager\n"
                "• Marketing Specialist\n"
                "• Sotuv menejeri\n"
                "• Buxgalter\n\n"
                "Yozing:",
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
                "📝 *Resume yaratish*\n\n"
                "Resume yozib beraman! Quyidagi ma'lumotlarni *bitta xabarda* yozing:\n\n"
                "1️⃣ *Ism familiya, telefon, email*\n"
                "2️⃣ *Ta'lim* (universitet, fakultet, yil)\n"
                "3️⃣ *Ish tajribasi* (kompaniya, lavozim, yil, asosiy ishlar)\n"
                "4️⃣ *Ko'nikmalar* (texnik + tillar)\n"
                "5️⃣ *Loyiha/sertifikatlar* (agar bor bo'lsa)\n\n"
                "Hammasini erkin shaklda yozing — men professional resume'ga aylantiraman.",
                reply_markup=get_back_to_menu_keyboard(lang),
                parse_mode="Markdown",
            )
            return

        if data == "career_review":
            context.user_data["mode"] = "career"
            context.user_data["career_action"] = "review"
            await query.edit_message_text(
                "🔍 *Resume tahlili*\n\n"
                "Hozirgi resume'ingizni shu yerga *to'liq* yozing yoki ko'chirib paste qiling.\n\n"
                "Men quyidagilarga e'tibor beraman:\n"
                "✓ ATS-friendly emasmi (robot tushunarmi)\n"
                "✓ Action verb va raqamlar\n"
                "✓ Format va tuzilish\n"
                "✓ Yaxshilash kerak bo'lgan joylar\n\n"
                "Resume'ni yozing:",
                reply_markup=get_back_to_menu_keyboard(lang),
                parse_mode="Markdown",
            )
            return

        if data == "career_interview":
            await query.edit_message_text(
                "🎤 *Intervyu mashqi*\n\n"
                "Qaysi turdagi savol bilan boshlaymiz?",
                reply_markup=kb_interview_type(),
                parse_mode="Markdown",
            )
            return

        if data.startswith("career_iq_"):
            qtype = data.replace("career_iq_", "")
            await query.edit_message_text("⏳ Savol tayyorlanyapti...")
            try:
                question = await _engine.generate_interview_question(profile, qtype, lang)
                context.user_data["interview_question"] = question
                context.user_data["mode"] = "career"
                context.user_data["career_action"] = "interview_answer"
                await query.edit_message_text(
                    f"{question}\n\n"
                    "💬 Javobingizni yozing — men professional baholashni beraman.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("⬅️ Orqaga", callback_data="career_back"),
                    ]]),
                    parse_mode="Markdown",
                )
            except Exception as e:
                logger.error(f"Interview question error: {e}")
                await query.edit_message_text(
                    "Savol tuzib bo'lmadi.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("⬅️ Orqaga", callback_data="career_back"),
                    ]]),
                )
            return

        if data == "career_chat":
            context.user_data["mode"] = "career"
            context.user_data["career_action"] = "chat"
            await query.edit_message_text(
                "💬 *Karyera bo'yicha maslahat*\n\n"
                "Har qanday savolingizni yozing:\n\n"
                "Misollar:\n"
                "• \"3 yil tajriba bilan qancha maoshi so'rasam bo'ladi?\"\n"
                "• \"IT sohaga qanday o'tsam bo'ladi?\"\n"
                "• \"LinkedIn profilim'ni qanday yaxshilash kerak?\"\n"
                "• \"Boshliqdan oshirish so'rashning to'g'ri yo'li nima?\"",
                reply_markup=get_back_to_menu_keyboard(lang),
                parse_mode="Markdown",
            )
            return

        if data == "career_salary":
            context.user_data["mode"] = "career"
            context.user_data["career_action"] = "chat"
            await query.edit_message_text(
                "💰 *Maosh muzokarasi*\n\n"
                "Quyidagilardan birini yozing:\n\n"
                "1. \"Hozir X so'm olaman, oshirish so'rasam bo'ladimi?\"\n"
                "2. \"Yangi ishga ofer berishdi, qanday kelishaman?\"\n"
                "3. \"Bozorda mening lavozim qancha to'lanadi?\"\n\n"
                "Aniq raqamlar va vaziyatni yozsangiz, aniq strategiya beraman.",
                reply_markup=get_back_to_menu_keyboard(lang),
                parse_mode="Markdown",
            )
            return

        if data == "career_plan":
            context.user_data["mode"] = "career"
            context.user_data["career_action"] = "chat"
            await query.edit_message_text(
                "📈 *6 oylik karyera rejasi*\n\n"
                "Aytib bering: hozirda qaysi bosqichdasiz va 6 oydan keyin "
                "qayerda bo'lishni xohlaysiz?\n\n"
                "Misol:\n"
                "_\"Hozir junior frontend, 6 oyda middle bo'lishni xohlayman\"_\n\n"
                "Men sizga aniq qadamlardan iborat reja tuzib beraman:\n"
                "• Qaysi ko'nikmani o'rganasiz\n"
                "• Qaysi loyiha qilasiz\n"
                "• Qaysi kursni olasiz\n"
                "• Qachon ish o'zgartirasiz\n\n"
                "Yozing:",
                reply_markup=get_back_to_menu_keyboard(lang),
                parse_mode="Markdown",
            )
            return

        if data == "career_setup":
            await query.edit_message_text(
                "⚙️ *Profilni qayta sozlash*\n\n"
                "Eski profilni o'chirib, qaytadan boshlaymizmi?",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ Ha, qaytadan", callback_data="career_reset_yes")],
                    [InlineKeyboardButton("❌ Bekor qilish", callback_data="career_back")],
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
            await query.edit_message_text("Xatolik yuz berdi.")
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

    # ── Wizard: target_role step ───────────────────────────────────
    if setup and setup.get("step") == "target_role":
        setup["target_role"] = text
        setup["step"] = "experience"
        context.user_data["career_setup"] = setup
        await message.reply_text(
            "⏱ *Tajribangiz necha yil?*\n\n"
            "Faqat raqam kiriting (masalan: `0`, `2`, `5`).\n"
            "Talaba yoki bitiruvchi bo'lsangiz `0` yozing.",
            parse_mode="Markdown",
        )
        return

    if setup and setup.get("step") == "experience":
        try:
            exp = int(text)
            if exp < 0 or exp > 60:
                raise ValueError
        except ValueError:
            await message.reply_text("❌ Iltimos, 0 dan 60 gacha bo'lgan raqam kiriting.")
            return

        # Save profile
        await upsert_career_profile(
            user_id=user.id,
            status=setup["status"],
            target_role=setup.get("target_role"),
            experience_years=exp,
        )
        context.user_data.pop("career_setup", None)
        lang = await user_service.get_user_language(user.id)
        profile = await get_career_profile(user.id)
        await message.reply_text(
            "✅ *Profilingiz tayyor!*\n\n"
            "Endi men sizning shaxsiy karyera koachingizman. Qani boshlaymiz!",
            parse_mode="Markdown",
        )
        await _show_career_dashboard(update, context, profile, lang, chat=update.effective_chat)
        return

    # ── Career actions ─────────────────────────────────────────────
    if context.user_data.get("mode") != "career":
        return

    profile = await get_career_profile(user.id)
    if not profile:
        await message.reply_text("Avval karyera profilini sozlang. /career")
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

    action = context.user_data.get("career_action", "chat")

    try:
        await message.chat.send_action("typing")

        if action == "resume":
            await message.reply_text("⏳ Resume yarataman, biroz kuting...")
            response = await _engine.generate_resume(profile, text, lang)
            # Save the generated resume
            await upsert_career_profile(
                user_id=user.id,
                status=profile["status"],
                resume_text=response,
            )
            await message.reply_text(
                response,
                reply_markup=get_back_to_menu_keyboard(lang),
                parse_mode="Markdown",
            )
            context.user_data.pop("career_action", None)

        elif action == "review":
            await message.reply_text("🔍 Resume'ni tahlil qilyapman...")
            history = await _memory.get_history(user.id, "career")
            await _memory.add_message(user.id, "career", "user", f"Mening resume'im:\n{text}\n\nTahlil qiling.")
            response = await _engine.process(
                message=f"Mening resume'im:\n{text}\n\nProfessional tahlil qiling: kuchli tomonlari, kamchiliklari, yaxshilash uchun aniq misollar.",
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
            await message.reply_text("🎯 Javobingizni baholayapman...")
            response = await _engine.evaluate_interview_answer(profile, question, text, lang)
            await message.reply_text(
                response,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🎤 Yana savol", callback_data="career_interview")],
                    [InlineKeyboardButton("⬅️ Orqaga", callback_data="career_back")],
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
        await message.reply_text("Texnik xatolik. Qaytadan urinib ko'ring.")
