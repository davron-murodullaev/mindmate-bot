"""
Statistics service
"""
from typing import Dict, Any
import logging

from mindmate.db.queries import (
    get_mood_stats,
    get_workout_stats,
    get_meditation_stats,
    get_expense_stats,
    get_expense_by_category
)

logger = logging.getLogger(__name__)


class StatsService:
    """Service for statistics and analytics."""

    @staticmethod
    async def get_mood_statistics(user_id: int, days: int = 7) -> Dict[str, int]:
        """Get mood statistics."""
        try:
            return await get_mood_stats(user_id, days)
        except Exception as e:
            logger.error(f"Error getting mood stats: {e}")
            return {}

    @staticmethod
    async def get_fitness_statistics(user_id: int, days: int = 7) -> Dict[str, Any]:
        """Get fitness statistics."""
        try:
            return await get_workout_stats(user_id, days)
        except Exception as e:
            logger.error(f"Error getting fitness stats: {e}")
            return {}

    @staticmethod
    async def get_meditation_statistics(user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get meditation statistics."""
        try:
            return await get_meditation_stats(user_id, days)
        except Exception as e:
            logger.error(f"Error getting meditation stats: {e}")
            return {}

    @staticmethod
    async def get_finance_statistics(user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get finance statistics."""
        try:
            stats = await get_expense_stats(user_id, days)
            categories = await get_expense_by_category(user_id, days)
            stats['categories'] = categories
            return stats
        except Exception as e:
            logger.error(f"Error getting finance stats: {e}")
            return {}


# Global service instance
stats_service = StatsService()
