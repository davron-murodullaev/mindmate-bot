"""
Conversation memory management
"""
from typing import List, Dict, Any, Optional
import logging

from mindmate.db.queries import (
    save_conversation_message,
    get_conversation_history,
    clear_conversation_history
)
from mindmate.core.constants import MAX_CONVERSATION_HISTORY

logger = logging.getLogger(__name__)


class ConversationMemory:
    """Manages conversation history for AI interactions."""

    def __init__(self, max_history: int = MAX_CONVERSATION_HISTORY):
        """
        Initialize conversation memory.

        Args:
            max_history: Maximum number of messages to keep in memory
        """
        self.max_history = max_history

    async def add_message(self, user_id: int, mode: str, role: str, content: str) -> None:
        """
        Add a message to conversation history.

        Args:
            user_id: User ID
            mode: AI mode (friend, healer, productivity)
            role: Message role (user or assistant)
            content: Message content
        """
        try:
            await save_conversation_message(user_id, mode, role, content)
        except Exception as e:
            logger.error(f"Error saving conversation message: {e}")

    async def get_history(
        self,
        user_id: int,
        mode: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """
        Get conversation history for a user in a specific mode.

        Args:
            user_id: User ID
            mode: AI mode
            limit: Maximum number of messages to retrieve

        Returns:
            List of messages in format [{"role": "user/assistant", "content": "..."}]
        """
        try:
            limit = limit or self.max_history
            history = await get_conversation_history(user_id, mode, limit)

            # Convert to format expected by AI
            messages = []
            for msg in history:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

            return messages

        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []

    async def clear_history(self, user_id: int, mode: str) -> None:
        """
        Clear conversation history for a user in a specific mode.

        Args:
            user_id: User ID
            mode: AI mode
        """
        try:
            await clear_conversation_history(user_id, mode)
            logger.info(f"Cleared conversation history for user {user_id} in mode {mode}")
        except Exception as e:
            logger.error(f"Error clearing conversation history: {e}")

    async def get_summary(self, user_id: int, mode: str) -> Optional[str]:
        """
        Get a summary of the conversation.

        Args:
            user_id: User ID
            mode: AI mode

        Returns:
            Summary string or None
        """
        try:
            history = await self.get_history(user_id, mode, limit=5)

            if not history:
                return None

            # Create a simple summary
            total_messages = len(history)
            user_messages = sum(1 for msg in history if msg["role"] == "user")
            assistant_messages = sum(1 for msg in history if msg["role"] == "assistant")

            return (
                f"Conversation summary:\n"
                f"Total messages: {total_messages}\n"
                f"Your messages: {user_messages}\n"
                f"AI responses: {assistant_messages}"
            )

        except Exception as e:
            logger.error(f"Error getting conversation summary: {e}")
            return None

    def format_history_for_display(self, history: List[Dict[str, str]]) -> str:
        """
        Format conversation history for display to user.

        Args:
            history: List of messages

        Returns:
            Formatted history string
        """
        if not history:
            return "No conversation history."

        formatted = "📜 Recent Conversation:\n\n"

        for msg in history[-5:]:  # Show last 5 messages
            role_emoji = "👤" if msg["role"] == "user" else "🤖"
            content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            formatted += f"{role_emoji} {content}\n\n"

        return formatted

    async def get_context_for_mode(self, user_id: int, mode: str) -> Dict[str, Any]:
        """
        Get contextual information for a specific mode.

        Args:
            user_id: User ID
            mode: AI mode

        Returns:
            Context dictionary
        """
        history = await self.get_history(user_id, mode)

        context = {
            "mode": mode,
            "message_count": len(history),
            "has_history": len(history) > 0,
            "last_topic": None
        }

        # Try to determine last topic from recent messages
        if history:
            recent_user_messages = [
                msg["content"] for msg in history
                if msg["role"] == "user"
            ]
            if recent_user_messages:
                context["last_topic"] = recent_user_messages[-1][:50]

        return context
