"""
Natural language reminder parser
"""
import re
from datetime import datetime, timedelta
from typing import Optional, Tuple
import logging

import pytz

logger = logging.getLogger(__name__)


def _now_for_tz(tz_name: Optional[str]) -> datetime:
    """Return current datetime in user's timezone (naive, for local comparisons)."""
    if tz_name:
        try:
            tz = pytz.timezone(tz_name)
            return datetime.now(tz).replace(tzinfo=None)
        except pytz.UnknownTimeZoneError:
            pass
    return datetime.now()


def parse_reminder(text: str, user_timezone: Optional[str] = None) -> Optional[Tuple[str, datetime, str]]:
    """
    Parse natural language reminder text.

    Args:
        text: Natural language reminder text

    Returns:
        Tuple of (reminder_text, reminder_time, repeat_type) or None if parsing fails
    """
    try:
        text = text.lower().strip()
        now = _now_for_tz(user_timezone)

        # Extract time-related patterns
        reminder_text = text
        reminder_time = None
        repeat_type = "once"

        # Pattern: "remind me to ... at HH:MM"
        time_pattern = r'at (\d{1,2}):?(\d{2})?\s*(am|pm)?'
        time_match = re.search(time_pattern, text)

        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.group(2) else 0
            am_pm = time_match.group(3)

            # Convert to 24-hour format
            if am_pm == 'pm' and hour != 12:
                hour += 12
            elif am_pm == 'am' and hour == 12:
                hour = 0

            reminder_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

            # Check for "tomorrow"
            if 'tomorrow' in text:
                reminder_time += timedelta(days=1)
            elif 'today' in text or reminder_time <= now:
                if reminder_time <= now:
                    reminder_time += timedelta(days=1)

            # Extract reminder text (remove time parts)
            reminder_text = re.sub(r'(remind me to|at \d{1,2}:?\d{0,2}\s*(am|pm)?|tomorrow|today)', '', text)
            reminder_text = reminder_text.strip()

        # Pattern: "in X minutes/hours"
        relative_pattern = r'in (\d+)\s*(minute|hour|day)s?'
        relative_match = re.search(relative_pattern, text)

        if relative_match and not reminder_time:
            amount = int(relative_match.group(1))
            unit = relative_match.group(2)

            if unit == 'minute':
                reminder_time = now + timedelta(minutes=amount)
            elif unit == 'hour':
                reminder_time = now + timedelta(hours=amount)
            elif unit == 'day':
                reminder_time = now + timedelta(days=amount)

            # Extract reminder text
            reminder_text = re.sub(r'(remind me to|in \d+\s*(minute|hour|day)s?)', '', text)
            reminder_text = reminder_text.strip()

        # Check for repeating patterns
        if 'every day' in text or 'daily' in text:
            repeat_type = 'daily'
        elif 'every week' in text or 'weekly' in text:
            repeat_type = 'weekly'
        elif 'every month' in text or 'monthly' in text:
            repeat_type = 'monthly'

        # Default to 1 hour from now if no time specified
        if not reminder_time:
            reminder_time = now + timedelta(hours=1)

        # Clean up reminder text
        reminder_text = re.sub(r'(every day|daily|every week|weekly|every month|monthly)', '', reminder_text)
        reminder_text = reminder_text.strip()

        if not reminder_text:
            reminder_text = "Reminder"

        return (reminder_text, reminder_time, repeat_type)

    except Exception as e:
        logger.error(f"Error parsing reminder: {e}")
        return None


def format_reminder_time(dt: datetime, user_timezone: Optional[str] = None) -> str:
    """Format reminder time for display."""
    now = _now_for_tz(user_timezone)

    if dt.date() == now.date():
        return f"Bugun soat {dt.strftime('%H:%M')}"
    elif dt.date() == (now + timedelta(days=1)).date():
        return f"Ertaga soat {dt.strftime('%H:%M')}"
    else:
        return dt.strftime('%Y-%m-%d %H:%M')


def validate_reminder_time(dt: datetime, user_timezone: Optional[str] = None) -> bool:
    """Validate that reminder time is in the future."""
    return dt > _now_for_tz(user_timezone)


def get_next_occurrence(dt: datetime, repeat_type: str) -> datetime:
    """
    Get next occurrence for repeating reminder.

    Args:
        dt: Current reminder datetime
        repeat_type: Type of repetition (once, daily, weekly, monthly)

    Returns:
        Next occurrence datetime
    """
    if repeat_type == 'daily':
        return dt + timedelta(days=1)
    elif repeat_type == 'weekly':
        return dt + timedelta(weeks=1)
    elif repeat_type == 'monthly':
        # Add approximately one month
        return dt + timedelta(days=30)
    else:
        # For 'once', return the same time (won't be rescheduled)
        return dt
