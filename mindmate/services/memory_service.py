"""
Memory service for AI conversations
"""
from typing import List, Dict, Any
import logging

from mindmate.ai.memory import ConversationMemory

logger = logging.getLogger(__name__)


class MemoryService:
    """Service for managing conversation memory."""

    def __init__(self):
        """Initialize memory service."""
        self.memory = ConversationMemory()

    async def save_message(
        self,
        user_id: int,
        mode: str,
        role: str,
        content: str
    ) -> None:
        """Save a conversation message."""
        await self.memory.add_message(user_id, mode, role, content)

    async def get_history(
        self,
        user_id: int,
        mode: str,
        limit: int = 20
    ) -> List[Dict[str, str]]:
        """Get conversation history."""
        return await self.memory.get_history(user_id, mode, limit)

    async def clear_history(self, user_id: int, mode: str) -> None:
        """Clear conversation history."""
        await self.memory.clear_history(user_id, mode)


# Global service instance
memory_service = MemoryService()
