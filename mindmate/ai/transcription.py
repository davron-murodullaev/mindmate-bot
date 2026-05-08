"""
Voice message transcription via OpenAI.

Strategy for better Uzbek/Russian/Mixed accuracy:
1. Try gpt-4o-mini-transcribe first (newer, better multilingual)
2. Fall back to whisper-1
3. Pass language hint + a prompt with our domain vocabulary so the model
   biases toward the words our users actually say.

Cost (approx):
  whisper-1               $0.006 / minute
  gpt-4o-mini-transcribe  $0.003 / minute (cheaper AND better quality)
"""
import io
import logging
from typing import Optional

from mindmate.core.config import settings

logger = logging.getLogger(__name__)


# Domain prompt: gives the transcriber expected vocabulary so it picks the
# right words when audio is noisy/accented. Mix of UZ/RU/EN reflects how
# people actually talk.
DOMAIN_PROMPT_UZ = (
    "MindMate AI yordamchi. Foydalanuvchi xabari quyidagi mavzularda bo'lishi mumkin: "
    "eslatma, kayfiyat, kundalik, imtihon, DTM, IELTS, karyera, resume, intervyu, "
    "stress, do'st topish, yordam, suhbat, samaradorlik. "
    "Misol: Ertaga soat 15:00 da suv ichish eslatmasini qo'shing. "
    "Bugun charchaganman. Imtihon mentorni oching. Eslatmalarimni o'chir."
)

DOMAIN_PROMPT_RU = (
    "MindMate ИИ помощник. Пользователь говорит о следующих темах: "
    "напоминания, настроение, дневник, экзамен, ДТМ, IELTS, карьера, резюме, "
    "собеседование, стресс, поиск друзей, помощь, разговор, продуктивность. "
    "Пример: Добавь напоминание выпить воду завтра в 15:00. "
    "Я устал сегодня. Открой ментора экзамена. Удали мои напоминания."
)


async def transcribe_voice(
    audio_bytes: bytes,
    filename: str = "voice.ogg",
    language_hint: Optional[str] = None,
) -> Optional[str]:
    """
    Transcribe voice to text via OpenAI.

    Args:
        audio_bytes: Raw audio bytes (Telegram voice = OGG/Opus).
        filename: Filename hint; extension matters for the API.
        language_hint: Optional ISO 639-1 code ("uz", "ru", "en"). When unset,
            the model auto-detects (best for mixed UZ/RU speech).

    Returns:
        Transcribed text, or None on failure.
    """
    if not settings.OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY not set — voice transcription unavailable")
        return None

    try:
        import openai
        client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        # Build domain prompt — biases the model toward our vocabulary.
        # Use UZ prompt when hinting Uzbek or auto, RU for Russian,
        # otherwise no prompt (English etc.).
        if language_hint == "ru":
            prompt = DOMAIN_PROMPT_RU
        elif language_hint == "en":
            prompt = ""  # English models are robust; prompt not needed
        else:
            # Default: bias toward Uzbek vocabulary
            prompt = DOMAIN_PROMPT_UZ

        # Try the newer model first — gpt-4o-mini-transcribe is cheaper AND
        # significantly better for non-English than whisper-1.
        text = await _transcribe_with_model(
            client, audio_bytes, filename,
            model="gpt-4o-mini-transcribe",
            language=language_hint,
            prompt=prompt,
        )
        if text:
            return text

        # Fallback to whisper-1 if newer model fails (model name typo, regional
        # availability, etc.)
        logger.info("Falling back to whisper-1 for transcription")
        text = await _transcribe_with_model(
            client, audio_bytes, filename,
            model="whisper-1",
            language=language_hint,
            prompt=prompt,
        )
        return text

    except Exception as e:
        logger.error(f"Voice transcription failed: {e}")
        return None


async def _transcribe_with_model(
    client,
    audio_bytes: bytes,
    filename: str,
    model: str,
    language: Optional[str],
    prompt: str,
) -> Optional[str]:
    """Send to OpenAI with a specific model. Returns None on per-model error."""
    try:
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = filename

        # Build kwargs — only include language/prompt when present (some models
        # reject empty strings).
        kwargs = {"model": model, "file": audio_file}
        if language:
            kwargs["language"] = language
        if prompt:
            kwargs["prompt"] = prompt

        response = await client.audio.transcriptions.create(**kwargs)
        text = (response.text or "").strip()
        if not text:
            return None

        # Sanity check: very short transcriptions of obviously-empty audio
        # sometimes produce noise like "thanks" or "..." — filter those.
        if len(text) < 2:
            return None

        return text

    except Exception as e:
        logger.warning(f"Transcription with {model} failed: {e}")
        return None
