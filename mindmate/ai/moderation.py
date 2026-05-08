"""
Image moderation via gpt-4o-mini vision.

Used before saving a profile photo to block NSFW / inappropriate content.

Cost: ~$0.001 per image. 1000 users × 3 photos = ~$3 total.
"""
import base64
import logging
from dataclasses import dataclass
from typing import Optional

from mindmate.core.config import settings

logger = logging.getLogger(__name__)


MODERATION_PROMPT = """You are moderating a photo for a public dating/friendship app.

Decide if the photo is appropriate for a public profile. Reply EXACTLY in this format:

APPROVED: yes|no
REASON: <one short sentence in Uzbek>

REJECT (APPROVED: no) if any of the following apply:
- Nudity, sexual content, or sexually suggestive poses
- Violence, weapons displayed prominently, blood
- Drugs, drug paraphernalia, alcohol bottles in foreground
- Hate symbols, extremist imagery
- Photo of someone obviously famous/celebrity (not the actual user)
- Pure logo, meme, screenshot, cartoon, anime — not a real person
- Heavily filtered, AI-generated face, or unrecognizable

ACCEPT (APPROVED: yes) if:
- Real person's photo (selfie or photographed)
- Casual, normal clothing or settings
- Group photos OK if person is identifiable
- Not necessarily the highest quality, just real and appropriate

For REASON write a friendly Uzbek sentence the user can read.
"""


@dataclass
class ModerationResult:
    approved: bool
    reason: str  # Localized message to show user


async def moderate_image(image_bytes: bytes) -> ModerationResult:
    """
    Run an image through content moderation. Returns approved flag + reason.

    Fail-open: if the moderation service fails, we approve so a transient
    OpenAI error doesn't block users. NSFW slips through but the alternative
    is breaking the entire upload flow on a network blip.
    """
    if not settings.OPENAI_API_KEY:
        return ModerationResult(approved=True, reason="")

    try:
        import openai
        client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        b64 = base64.b64encode(image_bytes).decode("ascii")

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": MODERATION_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                        },
                    ],
                },
            ],
            max_tokens=120,
            temperature=0.0,
        )

        content = response.choices[0].message.content or ""
        approved = _parse_approved(content)
        reason = _parse_reason(content)
        return ModerationResult(approved=approved, reason=reason)

    except Exception as e:
        logger.error(f"Moderation failed (fail-open): {e}")
        return ModerationResult(approved=True, reason="")


def _parse_approved(content: str) -> bool:
    for line in content.splitlines():
        line = line.strip()
        if line.upper().startswith("APPROVED:"):
            return "yes" in line.lower()
    # Conservative fallback: if model didn't follow format, approve
    return True


def _parse_reason(content: str) -> str:
    for line in content.splitlines():
        line = line.strip()
        if line.upper().startswith("REASON:"):
            return line.split(":", 1)[1].strip()
    return ""
