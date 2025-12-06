"""
ui/keyboards.py - Universal keyboard system for MindMate bot

This module provides keyboard builders for inline keyboards used across all handlers.
All text labels are retrieved using the get_text() function for multi-language support.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from mindmate.i18n import get_text


def get_main_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    """
    Build the main menu keyboard with all primary bot features.

    Args:
        lang: Language code (e.g., 'en', 'ru', 'uz')

    Returns:
        InlineKeyboardMarkup with main menu options
    """
    keyboard = [
        [
            InlineKeyboardButton(
                get_text(lang, "menu_mood"),
                callback_data="mood"
            ),
            InlineKeyboardButton(
                get_text(lang, "menu_journal"),
                callback_data="journal"
            ),
        ],
        [
            InlineKeyboardButton(
                get_text(lang, "menu_meditate"),
                callback_data="meditate"
            ),
            InlineKeyboardButton(
                get_text(lang, "menu_fitness"),
                callback_data="fitness"
            ),
        ],
        [
            InlineKeyboardButton(
                get_text(lang, "menu_healer"),
                callback_data="healer"
            ),
            InlineKeyboardButton(
                get_text(lang, "menu_stats"),
                callback_data="stats"
            ),
        ],
        [
            InlineKeyboardButton(
                get_text(lang, "menu_productivity"),
                callback_data="productivity"
            ),
            InlineKeyboardButton(
                get_text(lang, "menu_finance"),
                callback_data="finance"
            ),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


def get_back_keyboard(lang: str) -> InlineKeyboardMarkup:
    """
    Build a single 'Back' button keyboard.

    Args:
        lang: Language code (e.g., 'en', 'ru', 'uz')

    Returns:
        InlineKeyboardMarkup with a back button
    """
    keyboard = [
        [
            InlineKeyboardButton(
                f"◀️ {get_text(lang, 'back')}",
                callback_data="back"
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


def get_cancel_keyboard(lang: str) -> InlineKeyboardMarkup:
    """
    Build a single 'Cancel' button keyboard.

    Args:
        lang: Language code (e.g., 'en', 'ru', 'uz')

    Returns:
        InlineKeyboardMarkup with a cancel button
    """
    keyboard = [
        [
            InlineKeyboardButton(
                f"❌ {get_text(lang, 'cancel')}",
                callback_data="cancel"
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


def build_inline_keyboard(options: dict, lang: str, columns: int = 2) -> InlineKeyboardMarkup:
    """
    Build a custom inline keyboard from a dictionary of options.

    This is a flexible keyboard builder that converts a dictionary into an inline keyboard.
    The callback data is the dictionary key, and the button label is retrieved via get_text.

    Args:
        options: Dictionary mapping callback_data to translation keys
                 Example: {"mood": "menu_mood", "journal": "menu_journal"}
        lang: Language code (e.g., 'en', 'ru', 'uz')
        columns: Number of buttons per row (default: 2)

    Returns:
        InlineKeyboardMarkup with buttons arranged in rows

    Example:
        >>> options = {
        ...     "mood": "menu_mood",
        ...     "journal": "menu_journal",
        ...     "stats": "menu_stats"
        ... }
        >>> keyboard = build_inline_keyboard(options, "en", columns=2)
    """
    keyboard = []
    row = []

    for callback_data, text_key in options.items():
        button = InlineKeyboardButton(
            get_text(lang, text_key),
            callback_data=callback_data
        )
        row.append(button)

        # Create a new row when we reach the column limit
        if len(row) == columns:
            keyboard.append(row)
            row = []

    # Add remaining buttons if any
    if row:
        keyboard.append(row)

    return InlineKeyboardMarkup(keyboard)


# Additional helper functions for commonly used keyboards

def get_mood_keyboard(lang: str) -> InlineKeyboardMarkup:
    """
    Build mood tracking keyboard with 1-5 rating scale.

    Args:
        lang: Language code

    Returns:
        InlineKeyboardMarkup with mood options
    """
    keyboard = [
        [
            InlineKeyboardButton("😢 1", callback_data="mood_1"),
            InlineKeyboardButton("😟 2", callback_data="mood_2"),
            InlineKeyboardButton("😐 3", callback_data="mood_3"),
            InlineKeyboardButton("🙂 4", callback_data="mood_4"),
            InlineKeyboardButton("😊 5", callback_data="mood_5"),
        ],
        [
            InlineKeyboardButton(
                f"◀️ {get_text(lang, 'back')}",
                callback_data="back"
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


def get_confirmation_keyboard(lang: str) -> InlineKeyboardMarkup:
    """
    Build Yes/No confirmation keyboard.

    Args:
        lang: Language code

    Returns:
        InlineKeyboardMarkup with yes/no buttons
    """
    keyboard = [
        [
            InlineKeyboardButton(
                get_text(lang, "yes"),
                callback_data="confirm_yes"
            ),
            InlineKeyboardButton(
                get_text(lang, "no"),
                callback_data="confirm_no"
            ),
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


# Export all public functions
__all__ = [
    'get_main_menu_keyboard',
    'get_back_keyboard',
    'get_cancel_keyboard',
    'build_inline_keyboard',
    'get_mood_keyboard',
    'get_confirmation_keyboard',
]
