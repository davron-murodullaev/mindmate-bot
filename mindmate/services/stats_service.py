"""
Statistics service (simplified — mood + journal only)
"""
import logging
from typing import Dict, Any

from mindmate.db.queries import get_mood_stats, count_user_journals

logger = logging.getLogger(__name__)


class StatsService:
    """Service for statistics and analytics."""

    @staticmethod
    async def get_mood_statistics(user_id: int, days: int = 7) -> Dict[str, int]:
        """Get mood statistics for the last N days."""
        try:
            return await get_mood_stats(user_id, days)
        except Exception as e:
            logger.error(f"Error getting mood stats: {e}")
            return {}

    @staticmethod
    async def get_journal_count(user_id: int, days: int = 7) -> int:
        """Number of journal entries in the last N days."""
        try:
            return await count_user_journals(user_id, days)
        except Exception as e:
            logger.error(f"Error counting journal entries: {e}")
            return 0

    @staticmethod
    async def get_overall(user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get a one-shot overall summary."""
        try:
            mood_stats = await get_mood_stats(user_id, days)
            journal_count = await count_user_journals(user_id, days)
            return {
                "moods": sum(mood_stats.values()),
                "journals": journal_count,
                "chats": 0,  # populated by AI brain when added
            }
        except Exception as e:
            logger.error(f"Error getting overall stats: {e}")
            return {"moods": 0, "journals": 0, "chats": 0}


stats_service = StatsService()
