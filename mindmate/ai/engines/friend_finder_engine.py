"""
AI helper for friend-finding flows.

Two main jobs:
1. Generate a polished bio from the user's anketa data
2. Generate match icebreakers (3 personalized opening questions) when two
   users match — they don't have to wonder "what do I say first?"
"""
import logging
from typing import Dict, Any, List

from mindmate.ai.core import ai_core
from mindmate.core.constants import FRIEND_INTERESTS_LABELS_UZ, FRIEND_LOOKING_LABELS_UZ

logger = logging.getLogger(__name__)


async def write_bio(profile_data: Dict[str, Any], lang: str = "uz") -> str:
    """Generate an attractive 2-3 sentence bio from raw anketa data."""
    name = profile_data.get("display_name", "")
    age = profile_data.get("age", "")
    city = profile_data.get("city") or ""
    looking = FRIEND_LOOKING_LABELS_UZ.get(
        profile_data.get("looking_for", ""), profile_data.get("looking_for", "")
    )
    interests = profile_data.get("interests") or []
    interests_str = ", ".join(
        FRIEND_INTERESTS_LABELS_UZ.get(i, i) for i in interests
    )

    if lang == "ru":
        system = (
            "Ты пишешь короткое (2-3 предложения) био для профиля знакомств. "
            "Тон: лёгкий, искренний, без клише. Без эмодзи. Не используй "
            "слова \"ищу\", \"хочу найти\". Покажи характер через детали."
        )
        prompt = (
            f"Имя: {name}, возраст: {age}, город: {city}.\n"
            f"Цель: {looking}.\n"
            f"Интересы: {interests_str}.\n\n"
            "Напиши био (2-3 предложения), как будто это говорит сам человек."
        )
    elif lang == "en":
        system = (
            "Write a short (2-3 sentences) dating-profile bio. Tone: light, "
            "authentic, no clichés. No emoji. Don't use phrases like \"looking "
            "for\" — show personality through specific details."
        )
        prompt = (
            f"Name: {name}, age: {age}, city: {city}.\n"
            f"Goal: {looking}.\n"
            f"Interests: {interests_str}.\n\n"
            "Write a bio (2-3 sentences) as if the person is speaking."
        )
    else:
        system = (
            "Sen tanishuv anketasiga qisqa (2-3 jumla) bio yozasan. "
            "Ohang: yengil, samimiy, klishesiz. Emoji ishlatma. "
            "\"Izlayapman\" yoki \"topmoqchiman\" so'zlarini ishlatma — "
            "shaxsni aniq detallar orqali ko'rsat."
        )
        prompt = (
            f"Ism: {name}, yoshi: {age}, shahar: {city}.\n"
            f"Maqsad: {looking}.\n"
            f"Qiziqishlar: {interests_str}.\n\n"
            "Bio yoz (2-3 jumla) — go'yo shaxs o'zi gapirayotgandek."
        )

    try:
        return (await ai_core.generate_response(
            system_prompt=system,
            user_message=prompt,
            conversation_history=[],
            temperature=0.7,
            max_tokens=200,
        )).strip().strip('"').strip("'")
    except Exception as e:
        logger.error(f"Bio generation failed: {e}")
        # Fallback: build a simple bio without AI
        if interests_str:
            return f"{interests_str.split(',')[0].strip()} bilan qiziqaman. {city or 'Toshkent'}'da yashayman."
        return f"{name}, {age}. {city or 'Toshkent'}."


async def generate_icebreakers(
    me_profile: Dict[str, Any],
    other_profile: Dict[str, Any],
    lang: str = "uz",
) -> List[str]:
    """
    Generate 3 personalized opening questions for a match — based on
    the OTHER person's interests and bio, not generic "Hi how are you".
    """
    other_name = other_profile.get("display_name", "")
    other_interests = other_profile.get("interests") or []
    other_bio = other_profile.get("bio") or ""
    my_interests = me_profile.get("interests") or []
    shared = list(set(my_interests) & set(other_interests))

    interests_uz = ", ".join(
        FRIEND_INTERESTS_LABELS_UZ.get(i, i) for i in other_interests
    )
    shared_uz = ", ".join(
        FRIEND_INTERESTS_LABELS_UZ.get(i, i) for i in shared
    )

    if lang == "ru":
        system = (
            "Ты помогаешь начать разговор после совпадения. Сгенерируй 3 "
            "конкретных открывающих вопроса/реплики на основе профиля "
            "собеседника. Каждая — короткая (1 строка), искренняя, не "
            "клишированная. Без \"привет, как дела\"."
        )
        prompt = (
            f"Собеседник: {other_name}\n"
            f"Интересы: {interests_uz}\n"
            f"Био: {other_bio}\n"
            f"Общие интересы: {shared_uz or '—'}\n\n"
            "Дай 3 варианта начала разговора. Каждый на новой строке, без нумерации."
        )
    elif lang == "en":
        system = (
            "Help start a conversation after a match. Generate 3 specific "
            "openers based on the OTHER person's profile. Each one short "
            "(1 line), genuine, not a cliché. No 'hey how are you'."
        )
        prompt = (
            f"Match: {other_name}\n"
            f"Interests: {interests_uz}\n"
            f"Bio: {other_bio}\n"
            f"Shared interests: {shared_uz or '—'}\n\n"
            "Give 3 opener options. Each on a new line, no numbering."
        )
    else:
        system = (
            "Sen match bo'lganidan keyin suhbat boshlashga yordam berasan. "
            "Boshqa shaxsning anketasi asosida 3 ta aniq, qisqa boshlovchi "
            "savol/iboralarni yaratasan. Har biri 1 qator, samimiy, "
            "klishesiz. \"Salom, qalaysan\" emas."
        )
        prompt = (
            f"Yangi do'st: {other_name}\n"
            f"Qiziqishlari: {interests_uz}\n"
            f"Bio: {other_bio}\n"
            f"Umumiy qiziqishlaringiz: {shared_uz or '—'}\n\n"
            "3 ta suhbat boshlovchi variant ber. Har biri yangi qatorda, raqamlamasdan."
        )

    try:
        text = await ai_core.generate_response(
            system_prompt=system,
            user_message=prompt,
            conversation_history=[],
            temperature=0.8,
            max_tokens=250,
        )
        # Split into lines and clean
        lines = [l.strip().lstrip("•-*").lstrip("0123456789.").strip() for l in text.split("\n")]
        lines = [l for l in lines if l and len(l) > 5]
        return lines[:3] if lines else _fallback_icebreakers(other_profile)
    except Exception as e:
        logger.error(f"Icebreaker generation failed: {e}")
        return _fallback_icebreakers(other_profile)


def _fallback_icebreakers(other_profile: Dict[str, Any]) -> List[str]:
    """Static fallback openers when AI is unavailable."""
    name = other_profile.get("display_name", "do'stim")
    return [
        f"Salom {name}! Anketang menga yoqdi.",
        "Bu hafta nima yangiliklar?",
        "Bizdagi umumiy qiziqishlar haqida gaplashaylik!",
    ]
