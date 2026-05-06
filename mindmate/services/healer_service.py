"""
Healer service for mental health support.

Note: handlers now talk to the engine directly via ConversationMemory.
This thin service is kept only as a stable surface in case other code paths
import healer_service.
"""
import logging
from typing import Optional

from mindmate.ai.memory import ConversationMemory
from mindmate.ai.engines.healer_engine import HealerEngine
from mindmate.ai.formatter import format_response

logger = logging.getLogger(__name__)


class HealerService:
    """Service for healer mode interactions."""

    def __init__(self):
        self._memory = ConversationMemory()
        self._engine = HealerEngine()

    async def process_message(
        self, user_id: int, message: str, lang: Optional[str] = "en"
    ) -> str:
        """Process message in healer mode."""
        try:
            history = await self._memory.get_history(user_id, "healer")
            await self._memory.add_message(user_id, "healer", "user", message)

            response = await self._engine.process(
                message=message,
                history=history,
                context={"lang": lang},
            )

            await self._memory.add_message(user_id, "healer", "assistant", response)
            return format_response(response, mode="healer")

        except Exception as e:
            logger.error(f"Error in healer service: {e}")
            return "I'm here to support you. I'm experiencing a technical issue. Please try again."


healer_service = HealerService()
