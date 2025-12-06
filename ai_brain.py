"""
AI Brain - Central AI orchestration for MindMate Bot
"""
from typing import Optional, Dict, Any
import logging

from mindmate.ai.routing import route_to_engine
from mindmate.ai.memory import ConversationMemory
from mindmate.ai.formatter import format_response
from mindmate.core.config import settings

logger = logging.getLogger(__name__)


class AIBrain:
    """Central AI orchestration class."""

    def __init__(self):
        """Initialize AI brain."""
        self.memory = ConversationMemory()
        self.current_mode = "friend"

    async def process_message(
        self,
        user_id: int,
        message: str,
        mode: str = "friend",
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Process user message and generate AI response.

        Args:
            user_id: User ID
            message: User message
            mode: AI mode (friend, healer, productivity)
            context: Additional context data

        Returns:
            AI-generated response
        """
        try:
            # Update current mode
            self.current_mode = mode

            # Get conversation history
            history = await self.memory.get_history(user_id, mode)

            # Add current message to history
            await self.memory.add_message(user_id, mode, "user", message)

            # Route to appropriate AI engine
            response = await route_to_engine(
                mode=mode,
                message=message,
                history=history,
                context=context or {}
            )

            # Save AI response to memory
            await self.memory.add_message(user_id, mode, "assistant", response)

            # Format response
            formatted_response = format_response(response, mode)

            return formatted_response

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return "I'm having trouble processing your message right now. Please try again later."

    async def clear_context(self, user_id: int, mode: str) -> None:
        """
        Clear conversation context for a user in a specific mode.

        Args:
            user_id: User ID
            mode: AI mode
        """
        await self.memory.clear_history(user_id, mode)

    async def get_mode_info(self, mode: str) -> Dict[str, str]:
        """
        Get information about a specific AI mode.

        Args:
            mode: AI mode name

        Returns:
            Dictionary with mode information
        """
        modes = {
            "friend": {
                "name": "Friend",
                "description": "A supportive friend who listens and provides emotional support",
                "icon": "🤗"
            },
            "healer": {
                "name": "Healer",
                "description": "A mental health companion providing therapeutic guidance",
                "icon": "🧘"
            },
            "productivity": {
                "name": "Productivity Coach",
                "description": "A productivity expert helping you achieve your goals",
                "icon": "🎯"
            }
        }
        return modes.get(mode, modes["friend"])


# Global AI brain instance
ai_brain = AIBrain()
