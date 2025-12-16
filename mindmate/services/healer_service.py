"""
Healer service for mental health support
"""
import logging

from mindmate.ai_orchestrator import ai_orchestrator

logger = logging.getLogger(__name__)


class HealerService:
    """Service for healer mode interactions."""

    @staticmethod
    async def process_message(user_id: int, message: str) -> str:
        """
        Process message in healer mode.

        Args:
            user_id: User ID
            message: User message

        Returns:
            AI response
        """
        try:
            response = await ai_orchestrator.process_message(
                user_id=user_id,
                message=message,
                mode="healer"
            )
            return response

        except Exception as e:
            logger.error(f"Error in healer service: {e}")
            return "I'm here to support you. I'm experiencing a technical issue at the moment. Please try again."


# Global service instance
healer_service = HealerService()
