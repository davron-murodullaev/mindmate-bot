"""
Photo verification using gpt-4o vision.

Flow:
1. User has a profile photo (uploaded during anketa)
2. Bot asks for a fresh selfie ("show 2 fingers" or similar prompt)
3. We send both images to gpt-4o-mini and ask:
   - Is the same person in both photos?
   - Is the selfie a real fresh photo (matches the prompt)?
4. AI returns yes/no + a short note

Cost: gpt-4o-mini vision ≈ $0.001-0.003 per verification.
"""
import base64
import logging
from typing import Tuple, Optional

from mindmate.core.config import settings

logger = logging.getLogger(__name__)


VERIFICATION_PROMPT = (
    "You are verifying a profile photo. You see two images:\n"
    "1) The user's saved profile photo\n"
    "2) A fresh selfie they just took\n\n"
    "Decide:\n"
    "- Are these clearly the SAME person? (Same face, age range, features.)\n"
    "- Is image #2 a recent real selfie (not a screenshot, not from a magazine)?\n\n"
    "Respond in this exact format:\n"
    "VERIFIED: yes|no\n"
    "NOTE: <one short sentence>\n\n"
    "Be reasonable — slight lighting/angle differences are fine. "
    "Only mark unverified if the people clearly look different OR the second "
    "image is obviously not a fresh selfie."
)


async def verify_photos(
    profile_photo_bytes: bytes,
    selfie_bytes: bytes,
) -> Tuple[bool, str]:
    """
    Verify that the selfie matches the profile photo.

    Returns (is_verified, ai_note).
    """
    if not settings.OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY not set — verification unavailable")
        return False, "Tekshiruv xizmati hozir mavjud emas."

    try:
        import openai
        client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        profile_b64 = base64.b64encode(profile_photo_bytes).decode("ascii")
        selfie_b64 = base64.b64encode(selfie_bytes).decode("ascii")

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": VERIFICATION_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{profile_b64}"},
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{selfie_b64}"},
                        },
                    ],
                },
            ],
            max_tokens=200,
            temperature=0.1,
        )

        content = response.choices[0].message.content or ""
        is_verified = _parse_verified(content)
        note = _parse_note(content)
        return is_verified, note

    except Exception as e:
        logger.error(f"Photo verification failed: {e}")
        return False, "Tekshiruvda xatolik. Qaytadan urinib ko'ring."


def _parse_verified(content: str) -> bool:
    """Extract yes/no decision from AI response."""
    for line in content.splitlines():
        line = line.strip()
        if line.upper().startswith("VERIFIED:"):
            return "yes" in line.lower()
    # Fallback heuristic
    lower = content.lower()
    return "yes" in lower and "verified: no" not in lower


def _parse_note(content: str) -> str:
    """Extract the short note from AI response."""
    for line in content.splitlines():
        line = line.strip()
        if line.upper().startswith("NOTE:"):
            return line.split(":", 1)[1].strip()
    return content.strip()[:200]
