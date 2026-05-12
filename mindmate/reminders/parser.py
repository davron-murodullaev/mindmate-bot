"""
Natural language reminder parser — supports Uzbek, Russian, and English time expressions.
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


# ── Time extraction patterns (order matters — most specific first) ──────────

# Uzbek/Russian absolute: "soat 15:00", "15:00 da", "15:00", "в 15:00"
_ABS_TIME = re.compile(
    r'(?:soat\s*|в\s*|at\s*)?(\d{1,2})[:\.](\d{2})\s*(?:da|de|дa|de)?'
    r'|(?:soat\s*)(\d{1,2})\s*(?:da|de)?'
    r'|\bat\s*(\d{1,2}):?(\d{2})?\s*(am|pm)?',
    re.IGNORECASE,
)

# Relative: "2 soatdan keyin", "30 minutdan keyin", "в через 2 часа", "in 30 minutes"
_REL_TIME = re.compile(
    r'(?:in\s+|через\s+)?(\d+)\s*'
    r'(minut|daqiqa|minut|minute|minutes|soat|hour|hours|час|часа|часов|kun|day|days|день|дней)',
    re.IGNORECASE,
)

# "ertaga" / "завтра" / "tomorrow"
_TOMORROW = re.compile(r'\b(ertaga|bugun\s+kecha|завтра|tomorrow)\b', re.IGNORECASE)

# "bugun" / "сегодня" / "today"
_TODAY = re.compile(r'\b(bugun|сегодня|today)\b', re.IGNORECASE)

# Repeat patterns
_DAILY = re.compile(r'\b(har\s*kun|kunlik|daily|every\s*day|каждый\s*день|ежедневно)\b', re.IGNORECASE)
_WEEKLY = re.compile(r'\b(har\s*hafta|weekly|every\s*week|каждую\s*неделю|еженедельно)\b', re.IGNORECASE)
_MONTHLY = re.compile(r'\b(har\s*oy|monthly|every\s*month|каждый\s*месяц|ежемесячно)\b', re.IGNORECASE)

# Noise words to strip from reminder text
_NOISE = re.compile(
    r'\b(remind me to|eslatib qoy|eslatib qo\'y|напомни мне|'
    r'ertaga|bugun|завтра|сегодня|tomorrow|today|'
    r'har kun|kunlik|har hafta|har oy|daily|weekly|monthly|every\s+\w+|'
    r'каждый\s+\w+|ежедневно|еженедельно|ежемесячно|'
    r'в\s+\d{1,2}:\d{2}|at\s+\d{1,2}:?\d{0,2}\s*(?:am|pm)?|'
    r'soat\s*\d{1,2}(?::\d{2})?(?:\s*da)?|'
    r'(?:in|через)\s+\d+\s*\w+|'
    r'\d+\s*(?:minut|daqiqa|soat|hour|kun|day|min|час|минут|день)\w*'
    r')\b',
    re.IGNORECASE,
)


def _extract_time(text: str, now: datetime) -> Optional[datetime]:
    """Extract an absolute or relative time from text. Returns None if not found."""
    # 1) Relative time first ("in 30 minutes", "2 soatdan keyin")
    rel_m = _REL_TIME.search(text)
    if rel_m:
        amount = int(rel_m.group(1))
        unit = rel_m.group(2).lower()
        if unit in ('minut', 'daqiqa', 'minute', 'minutes', 'min', 'минут', 'минута', 'минуты'):
            return now + timedelta(minutes=amount)
        if unit in ('soat', 'hour', 'hours', 'час', 'часа', 'часов'):
            return now + timedelta(hours=amount)
        if unit in ('kun', 'day', 'days', 'день', 'дней', 'дня'):
            return now + timedelta(days=amount)

    # 2) Absolute time
    abs_m = _ABS_TIME.search(text)
    if abs_m:
        groups = abs_m.groups()
        # Pattern 1: HH:MM (with optional "da/в")
        if groups[0] and groups[1]:
            hour, minute = int(groups[0]), int(groups[1])
        # Pattern 2: soat HH (no minutes)
        elif groups[2]:
            hour, minute = int(groups[2]), 0
        # Pattern 3: English "at HH:MM am/pm"
        elif groups[3]:
            hour = int(groups[3])
            minute = int(groups[4]) if groups[4] else 0
            am_pm = groups[5]
            if am_pm and am_pm.lower() == 'pm' and hour != 12:
                hour += 12
            elif am_pm and am_pm.lower() == 'am' and hour == 12:
                hour = 0
        else:
            return None

        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            return None

        reminder_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        # Shift to tomorrow if time is in the past today
        if _TOMORROW.search(text):
            reminder_time += timedelta(days=1)
        elif reminder_time <= now:
            reminder_time += timedelta(days=1)

        return reminder_time

    return None


def parse_reminder(text: str, user_timezone: Optional[str] = None) -> Optional[Tuple[str, datetime, str]]:
    """
    Parse natural language reminder text (Uzbek, Russian, English).

    Returns:
        (reminder_text, reminder_time, repeat_type) or None on failure.
    """
    try:
        original = text.strip()
        lower = original.lower()
        now = _now_for_tz(user_timezone)

        # Detect repeat type
        if _DAILY.search(lower):
            repeat_type = "daily"
        elif _WEEKLY.search(lower):
            repeat_type = "weekly"
        elif _MONTHLY.search(lower):
            repeat_type = "monthly"
        else:
            repeat_type = "once"

        # Extract time
        reminder_time = _extract_time(lower, now)

        # Default: 1 hour from now
        if reminder_time is None:
            reminder_time = now + timedelta(hours=1)

        # Clean up reminder text
        reminder_text = _NOISE.sub(' ', original).strip()
        reminder_text = re.sub(r'\s{2,}', ' ', reminder_text).strip(' .,;:-')
        if not reminder_text:
            reminder_text = "Eslatma"

        return (reminder_text, reminder_time, repeat_type)

    except Exception as e:
        logger.error(f"Error parsing reminder: {e}")
        return None


def format_reminder_time(dt: datetime, user_timezone: Optional[str] = None) -> str:
    """Format reminder datetime for user-friendly display."""
    now = _now_for_tz(user_timezone)

    if dt.date() == now.date():
        return f"Bugun soat {dt.strftime('%H:%M')}"
    elif dt.date() == (now + timedelta(days=1)).date():
        return f"Ertaga soat {dt.strftime('%H:%M')}"
    else:
        return dt.strftime('%Y-%m-%d %H:%M')


def validate_reminder_time(dt: datetime, user_timezone: Optional[str] = None) -> bool:
    """Return True if the reminder time is in the future."""
    return dt > _now_for_tz(user_timezone)


def get_next_occurrence(dt: datetime, repeat_type: str) -> datetime:
    """Compute next occurrence for repeating reminders."""
    if repeat_type == "daily":
        return dt + timedelta(days=1)
    elif repeat_type == "weekly":
        return dt + timedelta(weeks=1)
    elif repeat_type == "monthly":
        return dt + timedelta(days=30)
    return dt
