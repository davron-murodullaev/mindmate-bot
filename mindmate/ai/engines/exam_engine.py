"""
Exam mentor AI engine — DTM, IELTS, SAT, Magistratura

Builds a per-user system prompt from their exam profile so responses
are personalized (target exam, subjects, days remaining, level).
"""
import logging
from datetime import date
from typing import List, Dict, Any, Optional

from mindmate.ai.core import ai_core

logger = logging.getLogger(__name__)


# Localized exam descriptions
EXAM_DESCRIPTIONS = {
    "dtm": "DTM (Davlat test markazi) — O'zbekiston Respublikasi oliy ta'lim muassasalariga kirish imtihoni",
    "ielts": "IELTS — International English Language Testing System",
    "sat": "SAT — Scholastic Assessment Test (chet el universitetlari)",
    "magistratura": "Magistratura kirish imtihoni (O'zbekiston)",
    "cefr": "CEFR — Common European Framework of Reference (chet tili sertifikati)",
}


SUBJECT_NAMES_UZ = {
    "matematika": "Matematika",
    "fizika": "Fizika",
    "kimyo": "Kimyo",
    "biologiya": "Biologiya",
    "tarix": "Tarix",
    "geografiya": "Geografiya",
    "adabiyot": "Adabiyot",
    "ona_tili": "Ona tili",
    "ingliz_tili": "Ingliz tili",
    "rus_tili": "Rus tili",
    "huquq": "Huquq",
    "informatika": "Informatika",
    "iqtisod": "Iqtisod",
}


def _days_until(exam_date: Optional[date]) -> Optional[int]:
    if not exam_date:
        return None
    today = date.today()
    delta = (exam_date - today).days
    return max(delta, 0)


def _build_system_prompt(profile: Dict[str, Any], lang: str = "uz") -> str:
    """Build a personalized system prompt from the user's exam profile."""
    exam_type = profile.get("exam_type", "dtm")
    subjects = profile.get("subjects") or []
    exam_date = profile.get("exam_date")
    target_score = profile.get("target_score") or "yuqori ball"
    level = profile.get("current_level") or "intermediate"
    days_left = _days_until(exam_date)

    exam_desc = EXAM_DESCRIPTIONS.get(exam_type, exam_type.upper())
    subjects_uz = ", ".join(SUBJECT_NAMES_UZ.get(s, s) for s in subjects) or "barcha fanlar"

    days_clause = (
        f"Imtihongacha {days_left} kun qoldi. " if days_left is not None
        else "Imtihon sanasi belgilanmagan. "
    )

    if lang == "ru":
        lang_instr = "Отвечай на русском языке, кратко и по делу."
    elif lang == "en":
        lang_instr = "Reply in English, concise and practical."
    else:
        lang_instr = "Javobni o'zbek tilida, qisqa va aniq ber."

    return f"""Sen — talabalar uchun shaxsiy imtihon mentorisan. Vazifang: foydalanuvchini imtihonga puxta tayyorlashga yordam berish.

Foydalanuvchi profili:
• Imtihon: {exam_desc}
• Fanlar: {subjects_uz}
• Maqsad: {target_score}
• Hozirgi daraja: {level}
• {days_clause}

Sening uslubing:
1. Aniq, qisqa, samarali — vaqtni tejash
2. Misollar bilan tushuntirish (formulalar, qoidalar)
3. O'rganish texnikalari (Pomodoro, Active recall, Spaced repetition)
4. Stressni boshqarish — ammo "psixolog" bo'lib qolma
5. Motivatsiya — haqiqiy, soxta emas
6. Foydalanuvchining maqsadi va kunlari soni asosida tavsiya ber

Foydalanuvchining maqsadi: {target_score}

QILMA:
• Uzun ma'ruza yozma — 2-4 paragraf yetadi
• "Imkonsiz" yoki "qiyin" deb umidni so'ndirma
• Soxta motivatsiya — faqat aniq strategiya

QILGIN:
• Aniq amaliy maslahat ber
• Kerak bo'lsa kun rejasi tuz
• Misollar bilan ko'rsat
• Ruhini ko'tar, lekin haqiqiy

{lang_instr}"""


class ExamEngine:
    """AI engine for exam mentor mode."""

    async def process(
        self,
        message: str,
        history: List[Dict[str, str]],
        context: Dict[str, Any],
    ) -> str:
        """Process a message in exam mentor mode."""
        try:
            profile = context.get("exam_profile") or {}
            lang = context.get("lang", "uz")
            system_prompt = _build_system_prompt(profile, lang)

            response = await ai_core.generate_response(
                system_prompt=system_prompt,
                user_message=message,
                conversation_history=history,
                temperature=0.5,  # Lower for accuracy on facts
            )
            return response
        except Exception as e:
            logger.error(f"Error in exam engine: {e}")
            return (
                "Texnik nosozlik yuz berdi. Qaytadan urinib ko'ring — "
                "imtihonga tayyorlanish davom etadi! 💪"
            )

    async def generate_daily_plan(
        self,
        profile: Dict[str, Any],
        lang: str = "uz",
    ) -> str:
        """Generate today's study plan based on user's profile."""
        days_left = _days_until(profile.get("exam_date"))
        subjects = profile.get("subjects") or []
        hours = profile.get("daily_study_hours", 4)

        subjects_str = ", ".join(SUBJECT_NAMES_UZ.get(s, s) for s in subjects) or "fanlar"

        days_context = (
            f"Imtihongacha {days_left} kun qoldi." if days_left is not None
            else "Imtihon sanasi noma'lum, umumiy reja tuz."
        )

        prompt = f"""Foydalanuvchi uchun BUGUNGI {hours} soatlik aniq o'qish rejasi tuz.

Konteks:
• {days_context}
• Fanlar: {subjects_str}
• Daraja: {profile.get('current_level', 'intermediate')}
• Maqsad: {profile.get('target_score', 'yuqori ball')}

Reja shaklida ber:
🌅 09:00–10:30 — [aniq mavzu] (Pomodoro 25/5)
☕ 10:30–10:45 — Tanaffus
🌅 10:45–12:00 — [aniq mavzu]
... va h.k.

Har blok uchun:
• Aniq mavzu/qoida nomini yoz
• Qaysi resursdan o'rganish (umumiy: darslik, video)
• Tanaffuslar bilan

Oxirida 1 jumla motivatsiya ber.
"""

        return await ai_core.generate_response(
            system_prompt=_build_system_prompt(profile, lang),
            user_message=prompt,
            conversation_history=[],
            temperature=0.4,
        )

    async def generate_practice_question(
        self,
        profile: Dict[str, Any],
        subject: str,
        lang: str = "uz",
    ) -> str:
        """Generate a practice question for a subject with detailed solution."""
        subject_name = SUBJECT_NAMES_UZ.get(subject, subject)
        prompt = f"""{subject_name} fanidan {profile.get('exam_type', 'DTM').upper()} darajasidagi 1 ta test savoli tuz.

Format:
**Savol:** [savol matni]

A) ...
B) ...
C) ...
D) ...

(Foydalanuvchi javobni yoborsin, sen baholaysan. Hozir to'g'ri javobni va tushuntirishni KO'RSATMA.)
"""
        return await ai_core.generate_response(
            system_prompt=_build_system_prompt(profile, lang),
            user_message=prompt,
            conversation_history=[],
            temperature=0.7,
        )
