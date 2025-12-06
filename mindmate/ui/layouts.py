"""
UI layouts and message formatting
"""
from typing import Dict, List, Any
from datetime import datetime

from mindmate.i18n import t


def format_mood_stats(stats: Dict[str, int], lang: str = "en", days: int = 7) -> str:
    """
    Format mood statistics for display.

    Args:
        stats: Dictionary of mood types and counts
        lang: Language code
        days: Number of days covered

    Returns:
        Formatted statistics string
    """
    if not stats:
        return t("mood.stats", lang, days=days) + "\n\nNo mood data available."

    text = t("mood.stats", lang, days=days) + "\n\n"

    # Sort by count
    sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)

    for mood_type, count in sorted_stats:
        emoji = get_mood_emoji(mood_type)
        text += f"{emoji} {mood_type.capitalize()}: {count}\n"

    return text


def format_workout_stats(stats: Dict[str, Any], lang: str = "en", days: int = 7) -> str:
    """
    Format workout statistics for display.

    Args:
        stats: Workout statistics dictionary
        lang: Language code
        days: Number of days covered

    Returns:
        Formatted statistics string
    """
    total = stats.get('total_workouts', 0)
    duration = stats.get('total_duration', 0) or 0
    avg = stats.get('avg_duration', 0) or 0

    return t("fitness.stats", lang, days=days, total=total, duration=int(duration), avg=int(avg))


def format_meditation_stats(stats: Dict[str, Any], lang: str = "en") -> str:
    """
    Format meditation statistics for display.

    Args:
        stats: Meditation statistics dictionary
        lang: Language code

    Returns:
        Formatted statistics string
    """
    total = stats.get('total_sessions', 0) or 0
    time = stats.get('total_duration', 0) or 0
    avg = stats.get('avg_duration', 0) or 0

    return t("meditation.stats", lang, total=int(total), time=int(time), avg=int(avg))


def format_finance_stats(stats: Dict[str, Any], lang: str = "en", days: int = 30) -> str:
    """
    Format finance statistics for display.

    Args:
        stats: Finance statistics dictionary
        lang: Language code
        days: Number of days covered

    Returns:
        Formatted statistics string
    """
    total = float(stats.get('total_amount', 0) or 0)
    avg = float(stats.get('avg_amount', 0) or 0)
    count = stats.get('total_expenses', 0) or 0

    return t("finance.stats", lang, days=days, total=f"{total:.2f}", avg=f"{avg:.2f}", count=count)


def format_expense_categories(categories: Dict[str, float], lang: str = "en") -> str:
    """
    Format expense categories for display.

    Args:
        categories: Dictionary of category names and amounts
        lang: Language code

    Returns:
        Formatted categories string
    """
    if not categories:
        return "No expenses recorded."

    # Sort by amount
    sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)

    categories_text = ""
    for category, amount in sorted_cats:
        categories_text += f"💰 {category.capitalize()}: ${amount:.2f}\n"

    return t("finance.by_category", lang, categories=categories_text)


def format_journal_entry(entry: Dict[str, Any], lang: str = "en") -> str:
    """
    Format a journal entry for display.

    Args:
        entry: Journal entry dictionary
        lang: Language code

    Returns:
        Formatted journal entry string
    """
    date = entry.get('created_at', datetime.now())
    if isinstance(date, datetime):
        date_str = date.strftime("%Y-%m-%d %H:%M")
    else:
        date_str = str(date)

    content = entry.get('content', '')

    return t("journal.entry", lang, date=date_str, content=content)


def format_reminder_notification(text: str, lang: str = "en") -> str:
    """
    Format a reminder notification.

    Args:
        text: Reminder text
        lang: Language code

    Returns:
        Formatted reminder notification
    """
    return t("reminders.notification", lang, text=text)


def get_mood_emoji(mood_type: str) -> str:
    """
    Get emoji for mood type.

    Args:
        mood_type: Mood type name

    Returns:
        Emoji character
    """
    mood_emojis = {
        "happy": "😊",
        "sad": "😢",
        "angry": "😠",
        "anxious": "😰",
        "tired": "😴",
        "excited": "🤗",
        "neutral": "😐",
        "stressed": "😫"
    }
    return mood_emojis.get(mood_type.lower(), "😊")


def format_list_with_numbers(items: List[str], start: int = 1) -> str:
    """
    Format a list with numbers.

    Args:
        items: List of items
        start: Starting number

    Returns:
        Formatted numbered list
    """
    return "\n".join([f"{i}. {item}" for i, item in enumerate(items, start=start)])


def format_progress_bar(current: int, total: int, length: int = 10) -> str:
    """
    Create a text-based progress bar.

    Args:
        current: Current value
        total: Total value
        length: Length of progress bar

    Returns:
        Progress bar string
    """
    if total == 0:
        percentage = 0
    else:
        percentage = min(current / total, 1.0)

    filled = int(length * percentage)
    bar = "█" * filled + "░" * (length - filled)

    return f"[{bar}] {int(percentage * 100)}%"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncating

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def format_datetime(dt: datetime, format_string: str = "%Y-%m-%d %H:%M") -> str:
    """
    Format datetime object.

    Args:
        dt: Datetime object
        format_string: Format string

    Returns:
        Formatted datetime string
    """
    return dt.strftime(format_string)
