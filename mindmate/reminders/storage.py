"""
Reminder storage utilities
"""
from typing import Dict, List, Any
from datetime import datetime
import logging

from mindmate.db.queries import (
    create_reminder,
    get_user_reminders,
    mark_reminder_sent,
    get_pending_reminders
)

logger = logging.getLogger(__name__)


class ReminderStorage:
    """Handles reminder storage operations."""

    @staticmethod
    async def save_reminder(
        user_id: int,
        text: str,
        reminder_time: datetime,
        repeat_type: str = "once"
    ) -> int:
        """
        Save a reminder to storage.

        Args:
            user_id: User ID
            text: Reminder text
            reminder_time: When to send the reminder
            repeat_type: Type of repetition (once, daily, weekly, monthly)

        Returns:
            Reminder ID
        """
        try:
            reminder_id = await create_reminder(
                user_id=user_id,
                text=text,
                reminder_time=reminder_time,
                repeat_type=repeat_type
            )
            logger.info(f"Saved reminder {reminder_id} for user {user_id}")
            return reminder_id

        except Exception as e:
            logger.error(f"Error saving reminder: {e}")
            raise

    @staticmethod
    async def get_reminders(user_id: int, include_sent: bool = False) -> List[Dict[str, Any]]:
        """
        Get user's reminders from storage.

        Args:
            user_id: User ID
            include_sent: Whether to include sent reminders

        Returns:
            List of reminder dictionaries
        """
        try:
            reminders = await get_user_reminders(user_id, include_sent)
            return reminders

        except Exception as e:
            logger.error(f"Error getting reminders: {e}")
            return []

    @staticmethod
    async def mark_as_sent(reminder_id: int) -> None:
        """
        Mark a reminder as sent.

        Args:
            reminder_id: Reminder ID
        """
        try:
            await mark_reminder_sent(reminder_id)
            logger.info(f"Marked reminder {reminder_id} as sent")

        except Exception as e:
            logger.error(f"Error marking reminder as sent: {e}")
            raise

    @staticmethod
    async def get_due_reminders(current_time: datetime) -> List[Dict[str, Any]]:
        """
        Get reminders that are due.

        Args:
            current_time: Current datetime

        Returns:
            List of due reminder dictionaries
        """
        try:
            reminders = await get_pending_reminders(current_time)
            return reminders

        except Exception as e:
            logger.error(f"Error getting due reminders: {e}")
            return []

    @staticmethod
    def calculate_next_occurrence(
        reminder_time: datetime,
        repeat_type: str
    ) -> datetime:
        """
        Calculate next occurrence for repeating reminders.

        Args:
            reminder_time: Current reminder time
            repeat_type: Type of repetition

        Returns:
            Next occurrence datetime
        """
        from mindmate.reminders.parser import get_next_occurrence
        return get_next_occurrence(reminder_time, repeat_type)


# Global storage instance
reminder_storage = ReminderStorage()
