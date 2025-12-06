"""
ui/layouts.py - UI Message Layout Templates for MindMate

This module provides formatted message layouts and templates for the bot.
All layouts support multi-language text via the i18n module.
"""

from mindmate.i18n import get_text


def get_welcome_layout(user_name: str, lang: str) -> str:
    """
    Generate welcome message layout for new users.

    Args:
        user_name: The user's first name
        lang: Language code (e.g., 'en', 'ru', 'uz')

    Returns:
        Formatted welcome message
    """
    welcome_text = get_text(lang, "welcome")
    return welcome_text


def get_main_menu_layout(lang: str) -> str:
    """
    Generate main menu message layout.

    Args:
        lang: Language code

    Returns:
        Formatted main menu message
    """
    return get_text(lang, "main_menu")


def get_stats_layout(stats_data: dict, lang: str) -> str:
    """
    Generate statistics display layout.

    Args:
        stats_data: Dictionary containing user statistics
        lang: Language code

    Returns:
        Formatted statistics message
    """
    title = get_text(lang, "stats_title")

    # Format statistics data
    stats_text = f"{title}\n\n"

    if "mood_entries" in stats_data:
        stats_text += f"📊 Mood Entries: {stats_data['mood_entries']}\n"

    if "journal_entries" in stats_data:
        stats_text += f"📝 Journal Entries: {stats_data['journal_entries']}\n"

    if "meditation_sessions" in stats_data:
        stats_text += f"🧘 Meditation Sessions: {stats_data['meditation_sessions']}\n"

    if "workout_sessions" in stats_data:
        stats_text += f"💪 Workout Sessions: {stats_data['workout_sessions']}\n"

    return stats_text


def get_journal_entry_layout(entry: dict, lang: str) -> str:
    """
    Generate journal entry display layout.

    Args:
        entry: Dictionary containing journal entry data
        lang: Language code

    Returns:
        Formatted journal entry message
    """
    date = entry.get("date", "Unknown")
    content = entry.get("content", "")
    mood = entry.get("mood", "")

    layout = f"📝 **Journal Entry** - {date}\n\n"

    if mood:
        layout += f"Mood: {mood}\n\n"

    layout += content

    return layout


def format_reminder_layout(reminder: dict, lang: str) -> str:
    """
    Generate reminder message layout.

    Args:
        reminder: Dictionary containing reminder data
        lang: Language code

    Returns:
        Formatted reminder message
    """
    title = reminder.get("title", "Reminder")
    time = reminder.get("time", "")
    message = reminder.get("message", "")

    layout = f"⏰ **{title}**\n\n"

    if time:
        layout += f"Time: {time}\n\n"

    layout += message

    return layout


def format_mood_prompt(lang: str) -> str:
    """
    Generate mood tracking prompt.

    Args:
        lang: Language code

    Returns:
        Formatted mood prompt message
    """
    return get_text(lang, "mood_ask")


def format_journal_prompt(lang: str) -> str:
    """
    Generate journal entry prompt.

    Args:
        lang: Language code

    Returns:
        Formatted journal prompt message
    """
    return get_text(lang, "journal_ask")


# Export all layout functions
__all__ = [
    'get_welcome_layout',
    'get_main_menu_layout',
    'get_stats_layout',
    'get_journal_entry_layout',
    'format_reminder_layout',
    'format_mood_prompt',
    'format_journal_prompt',
]
