"""
Healer mode AI engine
"""
import logging
from typing import List, Dict, Any

from mindmate.ai.core import ai_core

logger = logging.getLogger(__name__)


# Crisis keywords across English, Russian, and Uzbek (lowercased substrings)
CRISIS_KEYWORDS = {
    "en": [
        "suicide", "kill myself", "end my life", "want to die",
        "self-harm", "self harm", "hurt myself", "no reason to live",
        "i want to die", "ending it all",
    ],
    "ru": [
        "суицид", "самоубийств", "убить себя", "покончить с собой",
        "не хочу жить", "хочу умереть", "причинить себе вред",
        "нанести себе вред", "не вижу смысла жить",
    ],
    "uz": [
        "o'zimni o'ldir", "ozimni oldir", "o'zimga zarar",
        "yashashni xohlamayman", "o'lishni xohlayman", "olishni xohlayman",
        "hayotim ma'nosiz", "o'z joniga", "oz joniga",
    ],
}


# Crisis hotlines per language
CRISIS_RESPONSES = {
    "en": (
        "I'm deeply concerned about what you're sharing. Your life matters.\n\n"
        "🆘 Please reach out NOW:\n"
        "• 988 — Suicide & Crisis Lifeline (US)\n"
        "• Text HOME to 741741\n"
        "• findahelpline.com — international directory\n\n"
        "These services are free, confidential, and available 24/7.\n"
        "You don't have to face this alone. 💚"
    ),
    "ru": (
        "Мне очень важно то, что вы говорите. Ваша жизнь имеет значение.\n\n"
        "🆘 Пожалуйста, обратитесь СЕЙЧАС:\n"
        "• 8-800-2000-122 — Россия (бесплатно, круглосуточно)\n"
        "• 112 — экстренная служба\n"
        "• findahelpline.com — международный список\n\n"
        "Это бесплатно, конфиденциально и доступно 24/7.\n"
        "Вы не одни. 💚"
    ),
    "uz": (
        "Sizning so'zlaringizdan juda tashvishlanyapman. Hayotingiz qadrli.\n\n"
        "🆘 Iltimos, HOZIROQ murojaat qiling:\n"
        "• 1050 — O'zbekiston ishonch telefoni\n"
        "• 103 — Tez tibbiy yordam\n"
        "• findahelpline.com — xalqaro yordam\n\n"
        "Bu xizmatlar bepul, sirli va 24/7 ishlaydi.\n"
        "Yolg'iz emassiz. 💚"
    ),
}


def detect_crisis(message: str) -> bool:
    """Return True if the message contains crisis keywords in any supported language."""
    lower = message.lower()
    for keywords in CRISIS_KEYWORDS.values():
        if any(kw in lower for kw in keywords):
            return True
    return False


class HealerEngine:
    """AI engine for healer mode - mental health support and therapeutic guidance."""

    def __init__(self):
        self.system_prompt = """You are a compassionate mental health companion. Your role is to:

1. Provide a safe, non-judgmental space for users to express themselves
2. Listen deeply and validate their emotional experiences
3. Offer therapeutic insights and coping strategies
4. Help users explore their thoughts and feelings
5. Suggest evidence-based techniques for managing stress, anxiety, and difficult emotions
6. Encourage self-reflection and personal growth
7. Recognize when professional help may be needed

Communication style:
- Use calm, soothing language
- Be patient and present
- Ask open-ended questions to facilitate exploration
- Reflect back what you hear to show understanding
- Provide gentle guidance without being prescriptive
- Keep responses thoughtful and measured (2-4 paragraphs)
- Respond in the same language the user writes in (English, Russian, or Uzbek)

Techniques to draw from:
- Cognitive Behavioral Therapy (CBT) principles
- Mindfulness and grounding techniques
- Emotional regulation strategies
- Positive psychology approaches

IMPORTANT: You are a supportive companion, not a replacement for professional mental health care.
If someone expresses thoughts of self-harm or suicide, encourage them to seek immediate professional help."""

    async def process(
        self,
        message: str,
        history: List[Dict[str, str]],
        context: Dict[str, Any],
    ) -> str:
        """Process user message in healer mode."""
        try:
            # Crisis detection across supported languages
            if detect_crisis(message):
                lang = (context or {}).get("lang", "en")
                return CRISIS_RESPONSES.get(lang, CRISIS_RESPONSES["en"])

            response = await ai_core.generate_response(
                system_prompt=self.system_prompt,
                user_message=message,
                conversation_history=history,
                temperature=0.7,
            )
            return response

        except Exception as e:
            logger.error(f"Error in healer engine: {e}")
            return (
                "I'm here to support you. I'm experiencing a technical issue at "
                "the moment, but your feelings matter. Please try again shortly."
            )
