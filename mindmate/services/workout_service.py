"""
Workout service
"""
from typing import List, Dict, Any
import logging

from mindmate.db.queries import create_workout, get_user_workouts, get_workout_stats

logger = logging.getLogger(__name__)


class WorkoutService:
    """Service for workout tracking."""

    @staticmethod
    async def log_workout(
        user_id: int,
        activity_type: str,
        duration: int,
        calories: int = None,
        notes: str = None
    ) -> int:
        """Log a workout."""
        try:
            workout_id = await create_workout(user_id, activity_type, duration, calories, notes)
            logger.info(f"Logged workout {workout_id} for user {user_id}")
            return workout_id
        except Exception as e:
            logger.error(f"Error logging workout: {e}")
            raise

    @staticmethod
    async def get_workouts(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user's workouts."""
        try:
            return await get_user_workouts(user_id, limit)
        except Exception as e:
            logger.error(f"Error getting workouts: {e}")
            return []

    @staticmethod
    async def get_stats(user_id: int, days: int = 7) -> Dict[str, Any]:
        """Get workout statistics."""
        try:
            return await get_workout_stats(user_id, days)
        except Exception as e:
            logger.error(f"Error getting workout stats: {e}")
            return {}


# Global service instance
workout_service = WorkoutService()
