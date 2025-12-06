"""
Reminder service
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

from mindmate.db.queries import create_reminder, get_user_reminders
from mindmate.reminders.parser import parse_reminder, format_reminder_time, validate_reminder_time

logger = logging.getLogger(__name__)


class ReminderService:
    """Service for managing reminders."""

    @staticmethod
    async def create_from_text(user_id: int, text: str) -> Optional[Dict[str, Any]]:
        """
        Create a reminder from natural language text.

        Args:
            user_id: User ID
            text: Natural language reminder text

        Returns:
            Dictionary with reminder details or None if parsing fails
        """
        try:
            parsed = parse_reminder(text)

            if not parsed:
                return None

            reminder_text, reminder_time, repeat_type = parsed

            # Validate time is in the future
            if not validate_reminder_time(reminder_time):
                return {
                    'error': 'Reminder time must be in the future'
                }

            # Create reminder in database
            reminder_id = await create_reminder(
                user_id=user_id,
                text=reminder_text,
                reminder_time=reminder_time,
                repeat_type=repeat_type
            )

            return {
                'id': reminder_id,
                'text': reminder_text,
                'time': reminder_time,
                'formatted_time': format_reminder_time(reminder_time),
                'repeat_type': repeat_type
            }

        except Exception as e:
            logger.error(f"Error creating reminder: {e}")
            return None

    @staticmethod
    async def get_user_reminders_list(
        user_id: int,
        include_sent: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get list of user's reminders.

        Args:
            user_id: User ID
            include_sent: Whether to include sent reminders

        Returns:
            List of reminder dictionaries
        """
        try:
            reminders = await get_user_reminders(user_id, include_sent)

            # Format for display
            formatted = []
            for reminder in reminders:
                formatted.append({
                    'id': reminder['id'],
                    'text': reminder['text'],
                    'time': reminder['reminder_time'],
                    'formatted_time': format_reminder_time(reminder['reminder_time']),
                    'repeat_type': reminder['repeat_type'],
                    'is_sent': reminder['is_sent']
                })

            return formatted

        except Exception as e:
            logger.error(f"Error getting user reminders: {e}")
            return []

    @staticmethod
    def format_reminders_list(reminders: List[Dict[str, Any]]) -> str:
        """
        Format reminders list for display.

        Args:
            reminders: List of reminder dictionaries

        Returns:
            Formatted string
        """
        if not reminders:
            return "You don't have any reminders set."

        text = "📋 Your Reminders:\n\n"

        for i, reminder in enumerate(reminders, 1):
            status = "✅" if reminder['is_sent'] else "⏰"
            repeat = f" ({reminder['repeat_type']})" if reminder['repeat_type'] != 'once' else ""

            text += f"{status} {i}. {reminder['text']}\n"
            text += f"   {reminder['formatted_time']}{repeat}\n\n"

        return text


# Global service instance
reminder_service = ReminderService()
