"""
Voice message transcription via OpenAI Whisper.

Cost: ~$0.006 / minute → very cheap. Whisper handles Telegram's .ogg/.oga
files natively. Falls back gracefully if no OpenAI key is configured.
"""
import io
import logging
from typing import Optional

from mindmate.core.config import settings

logger = logging.getLogger(__name__)


async def transcribe_voice(audio_bytes: bytes, filename: str = "voice.ogg") -> Optional[str]:
    """
    Transcribe a voice message to text using OpenAI Whisper.

    Args:
        audio_bytes: Raw audio bytes (Telegram voice format = OGG/Opus)
        filename: Filename hint for the API (extension matters)

    Returns:
        Transcribed text, or None on failure.
    """
    if not settings.OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY not set — voice transcription unavailable")
        return None

    try:
        import openai
        client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        # Whisper expects a file-like object with a name
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = filename

        response = await client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            # Don't restrict language — Whisper auto-detects (better for UZ/RU mixed)
        )
        return response.text

    except Exception as e:
        logger.error(f"Voice transcription failed: {e}")
        return None
