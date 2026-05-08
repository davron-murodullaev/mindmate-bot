"""
Career coach AI engine — resume, interview, salary negotiation, career planning.

Builds a personalized system prompt from the user's career profile.
"""
import logging
from typing import List, Dict, Any, Optional

from mindmate.ai.core import ai_core

logger = logging.getLogger(__name__)


CAREER_STATUSES = {
    "student": "Talaba (hali ishlamayman)",
    "graduate": "Bitiruvchi, ish izlamoqdaman",
    "employed": "Hozirda ishlayapman",
    "switching": "Ish o'zgartirmoqchiman",
    "freelance": "Freelancer / o'z biznes",
}


def _build_system_prompt(profile: Dict[str, Any], lang: str = "uz") -> str:
    status_label = CAREER_STATUSES.get(profile.get("status", ""), "noma'lum")
    target_role = profile.get("target_role") or "aniqlanmagan"
    industry = profile.get("industry") or "har xil"
    exp = profile.get("experience_years", 0)
    skills = ", ".join(profile.get("skills") or []) or "kiritilmagan"

    if lang == "ru":
        lang_instr = "Отвечай на русском языке, профессионально и кратко."
    elif lang == "en":
        lang_instr = "Reply in English, professional and concise."
    else:
        lang_instr = "Javobni o'zbek tilida, professional va aniq ber."

    return f"""Sen — yosh mutaxassislar uchun karyera koachi va HR mutaxassisisan. Vazifang: foydalanuvchiga yaxshi ish topish, karyerada o'sish va martaba qurishga yordam berish.

Foydalanuvchi profili:
• Holati: {status_label}
• Maqsad lavozim: {target_role}
• Soha: {industry}
• Tajriba: {exp} yil
• Ko'nikmalar: {skills}

Sening uslubing:
1. Professional, lekin samimiy
2. Aniq, amaliy maslahat (umumiy nasihatlar emas)
3. Bozor haqiqatlari — masalan UZ ish bozori, IT/non-IT ayrimliklari
4. Real misollar bilan
5. Foydalanuvchini "tayyor mahsulot" sifatida o'ylash — savol berib, kerakli ma'lumotni ol

QILGIN:
• Aniq harakat reja ber
• "Birinchi qadam" har doim ko'rsat
• ATS-friendly resume yozishga o'rgat
• Maoshni qanday so'rashni o'rgat (haqiqiy raqamlar, UZ kontekstida)
• LinkedIn/HH/Glassdoor strategiyasi

QILMA:
• Soxta optimizm ("hammasi yaxshi bo'ladi")
• Umumiy "harder work" maslahatlar
• Ko'p ma'lumot bir paytda — bosqichma-bosqich

{lang_instr}"""


class CareerEngine:
    """AI engine for career coach mode."""

    async def process(
        self,
        message: str,
        history: List[Dict[str, str]],
        context: Dict[str, Any],
    ) -> str:
        try:
            profile = context.get("career_profile") or {}
            lang = context.get("lang", "uz")
            system_prompt = _build_system_prompt(profile, lang)

            response = await ai_core.generate_response(
                system_prompt=system_prompt,
                user_message=message,
                conversation_history=history,
                temperature=0.6,
            )
            return response
        except Exception as e:
            logger.error(f"Error in career engine: {e}")
            return (
                "Texnik xatolik. Qaytadan urinib ko'ring — "
                "yaxshi ishni topish jarayoni davom etadi! 💼"
            )

    async def generate_resume(
        self,
        profile: Dict[str, Any],
        user_input: str,
        lang: str = "uz",
    ) -> str:
        """Generate a resume from user-provided info."""
        target = profile.get("target_role") or "noma'lum"
        exp_years = profile.get("experience_years", 0)
        skills_list = profile.get("skills") or []
        skills_str = ", ".join(skills_list) if skills_list else "noma'lum"

        prompt = f"""Foydalanuvchining ma'lumotlari asosida professional, ATS-friendly resume yoz.

Foydalanuvchi yozgan ma'lumot:
{user_input}

Profil ma'lumotlari:
• Maqsad: {target}
• Tajriba: {exp_years} yil
• Ko'nikmalar: {skills_str}

Resume tuzilishi:
👤 ISM FAMILIYA
Lavozim | shahar | telefon | email | LinkedIn

📌 SUMMARY (3 jumla)
[O'zining kim ekanligi, asosiy kuchi, maqsadi]

💼 ISH TAJRIBASI
**Lavozim** | Kompaniya | yil-yil
• Action verb bilan boshlangan natija (raqamlar bilan)
• 2-3 ta bullet har bir ish uchun

🎓 TA'LIM
**Daraja** | Universitet | yil

🛠 KO'NIKMALAR
[Texnik | Tillar | Soft skills]

🏆 LOYIHA / SERTIFIKAT (agar bor bo'lsa)

KO'RSATMA:
• ATS uchun toza format (jadval/grafika ishlatma)
• Action verb bilan boshlash (Yaratdim, Boshqardim, Optimizatsiya qildim)
• Raqamlar bilan natijalar (% ortdi, X marta tezroq, $Y tejandi)
• 1 sahifaga sig'sin
• UZ bozoriga moslashtir
"""
        return await ai_core.generate_response(
            system_prompt=_build_system_prompt(profile, lang),
            user_message=prompt,
            conversation_history=[],
            temperature=0.5,
            max_tokens=3000,
        )

    async def generate_interview_question(
        self,
        profile: Dict[str, Any],
        question_type: str = "general",
        lang: str = "uz",
    ) -> str:
        """Generate an interview question based on user's target role."""
        target = profile.get("target_role") or "umumiy lavozim"

        type_hint = {
            "general": "umumiy savol (HR savoli)",
            "technical": "texnik savol (target_role bo'yicha)",
            "behavioral": "STAR formatdagi xulq-atvor savoli",
            "salary": "maosh haqida savol",
        }.get(question_type, "umumiy savol")

        prompt = f"""Foydalanuvchi {target} lavozimiga intervyu beryapti. Unga 1 ta {type_hint} savol ber.

Format:
**Savol:** [savol matni]

(Foydalanuvchi o'z javobini yozsin, men keyin baholashim mumkin.)
"""
        return await ai_core.generate_response(
            system_prompt=_build_system_prompt(profile, lang),
            user_message=prompt,
            conversation_history=[],
            temperature=0.7,
        )

    async def evaluate_interview_answer(
        self,
        profile: Dict[str, Any],
        question: str,
        answer: str,
        lang: str = "uz",
    ) -> str:
        """Evaluate user's answer to an interview question."""
        prompt = f"""Intervyu savoliga foydalanuvchining javobini baholash.

**Savol:** {question}

**Javob:** {answer}

Baholash strukturasi:
✅ Yaxshi tomonlar (1-3 ta)
⚠️ Yaxshilash kerak (1-3 ta, aniq misollar bilan)
💡 Yaxshilangan namuna javob (qisqa)
🎯 Umumiy ball: X/10

Konstruktiv bo'l. STAR (Situation, Task, Action, Result) framework'iga moslashishni tavsiya qil.
"""
        return await ai_core.generate_response(
            system_prompt=_build_system_prompt(profile, lang),
            user_message=prompt,
            conversation_history=[],
            temperature=0.5,
        )
