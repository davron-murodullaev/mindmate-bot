"""
UI layouts and message formatting (simplified).
"""
from typing import Dict, Any, List
from datetime import datetime

from mindmate.i18n import t
from mindmate.core.constants import MOOD_EMOJIS


def format_mood_stats(stats: Dict[str, int], lang: str = "en", days: int = 7) -> str:
    """Format mood statistics for display."""
    if not stats:
        return t("mood.no_data", lang)

    text = t("mood.stats", lang).format(days=days) + "\n\n"
    sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)
    for mood_type, count in sorted_stats:
        emoji = MOOD_EMOJIS.get(mood_type, "😊")
        text += f"{emoji} {mood_type.capitalize()}: {count}\n"
    return text


def format_journal_entry(entry: Dict[str, Any], lang: str = "en") -> str:
    """Format a journal entry for display."""
    date = entry.get("created_at", datetime.now())
    if isinstance(date, datetime):
        date_str = date.strftime("%Y-%m-%d %H:%M")
    else:
        date_str = str(date)

    content = entry.get("content", "")
    return t("journal.entry", lang).format(date=date_str, content=content)


def format_reminder_notification(text: str, lang: str = "en") -> str:
    """Format a reminder notification."""
    return t("reminders.notification", lang).format(text=text)


def format_list_with_numbers(items: List[str], start: int = 1) -> str:
    """Format a list with numbers."""
    return "\n".join([f"{i}. {item}" for i, item in enumerate(items, start=start)])


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to a maximum length."""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def format_datetime(dt: datetime, format_string: str = "%Y-%m-%d %H:%M") -> str:
    """Format datetime object."""
    return dt.strftime(format_string)
