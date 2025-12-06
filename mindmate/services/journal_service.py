"""
Journal service
"""
from typing import List, Dict, Any
import logging

from mindmate.db.queries import create_journal, get_user_journals

logger = logging.getLogger(__name__)


class JournalService:
    """Service for journal management."""

    @staticmethod
    async def create_entry(
        user_id: int,
        content: str,
        mood: str = None
    ) -> int:
        """Create a journal entry."""
        try:
            entry_id = await create_journal(user_id, content, mood)
            logger.info(f"Created journal entry {entry_id} for user {user_id}")
            return entry_id
        except Exception as e:
            logger.error(f"Error creating journal entry: {e}")
            raise

    @staticmethod
    async def get_entries(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user's journal entries."""
        try:
            return await get_user_journals(user_id, limit)
        except Exception as e:
            logger.error(f"Error getting journal entries: {e}")
            return []


# Global service instance
journal_service = JournalService()
