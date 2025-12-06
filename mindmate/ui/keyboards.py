"""
Keyboard builders for MindMate Bot
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from typing import List, Optional

from mindmate.i18n import t
from mindmate.core.constants import (
    SUPPORTED_LANGUAGES,
    MOOD_EMOJIS,
    MEDITATION_DURATIONS,
    STATS_PERIODS
)


def get_language_keyboard() -> InlineKeyboardMarkup:
    """Get language selection keyboard."""
    keyboard = [
        [
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        ],
        [
            InlineKeyboardButton("🇺🇿 O'zbek", callback_data="lang_uz"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_setup_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Get setup completion keyboard."""
    keyboard = [
        [InlineKeyboardButton(
            t("buttons.confirm", lang),
            callback_data="setup_complete"
        )]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_main_menu_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Get main menu keyboard."""
    keyboard = [
        [
            InlineKeyboardButton(
                t("menu.mood_tracking", lang),
                callback_data="menu_mood"
            ),
            InlineKeyboardButton(
                t("menu.meditation", lang),
                callback_data="menu_meditation"
            ),
        ],
        [
            InlineKeyboardButton(
                t("menu.fitness", lang),
                callback_data="menu_fitness"
            ),
            InlineKeyboardButton(
                t("menu.journal", lang),
                callback_data="menu_journal"
            ),
        ],
        [
            InlineKeyboardButton(
                t("menu.healer", lang),
                callback_data="menu_healer"
            ),
            InlineKeyboardButton(
                t("menu.productivity", lang),
                callback_data="menu_productivity"
            ),
        ],
        [
            InlineKeyboardButton(
                t("menu.finance", lang),
                callback_data="menu_finance"
            ),
            InlineKeyboardButton(
                t("menu.stats", lang),
                callback_data="menu_stats"
            ),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_mood_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Get mood selection keyboard."""
    keyboard = [
        [
            InlineKeyboardButton(
                f"{MOOD_EMOJIS['happy']} {t('mood.happy', lang)}",
                callback_data="mood_happy"
            ),
            InlineKeyboardButton(
                f"{MOOD_EMOJIS['sad']} {t('mood.sad', lang)}",
                callback_data="mood_sad"
            ),
        ],
        [
            InlineKeyboardButton(
                f"{MOOD_EMOJIS['angry']} {t('mood.angry', lang)}",
                callback_data="mood_angry"
            ),
            InlineKeyboardButton(
                f"{MOOD_EMOJIS['anxious']} {t('mood.anxious', lang)}",
                callback_data="mood_anxious"
            ),
        ],
        [
            InlineKeyboardButton(
                f"{MOOD_EMOJIS['tired']} {t('mood.tired', lang)}",
                callback_data="mood_tired"
            ),
            InlineKeyboardButton(
                f"{MOOD_EMOJIS['excited']} {t('mood.excited', lang)}",
                callback_data="mood_excited"
            ),
        ],
        [
            InlineKeyboardButton(
                t("buttons.back", lang),
                callback_data="menu_main"
            ),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_meditation_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Get meditation duration selection keyboard."""
    keyboard = []

    # Add duration buttons
    row = []
    for duration in MEDITATION_DURATIONS:
        row.append(InlineKeyboardButton(
            t(f"meditation.duration_{duration}", lang),
            callback_data=f"duration_{duration}"
        ))
        if len(row) == 2:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    # Add back button
    keyboard.append([
        InlineKeyboardButton(
            t("buttons.back", lang),
            callback_data="menu_main"
        )
    ])

    return InlineKeyboardMarkup(keyboard)


def get_fitness_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Get fitness menu keyboard."""
    keyboard = [
        [
            InlineKeyboardButton(
                t("fitness.log_workout", lang),
                callback_data="fitness_log"
            ),
        ],
        [
            InlineKeyboardButton(
                t("fitness.view_stats", lang),
                callback_data="fitness_stats"
            ),
        ],
        [
            InlineKeyboardButton(
                t("buttons.back", lang),
                callback_data="menu_main"
            ),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_journal_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Get journal menu keyboard."""
    keyboard = [
        [
            InlineKeyboardButton(
                t("journal.new_entry", lang),
                callback_data="journal_new"
            ),
        ],
        [
            InlineKeyboardButton(
                t("journal.view_entries", lang),
                callback_data="journal_view"
            ),
        ],
        [
            InlineKeyboardButton(
                t("buttons.back", lang),
                callback_data="menu_main"
            ),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_finance_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Get finance menu keyboard."""
    keyboard = [
        [
            InlineKeyboardButton(
                t("finance.add_expense", lang),
                callback_data="finance_add"
            ),
        ],
        [
            InlineKeyboardButton(
                t("finance.view_stats", lang),
                callback_data="finance_stats"
            ),
        ],
        [
            InlineKeyboardButton(
                t("buttons.back", lang),
                callback_data="menu_main"
            ),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_stats_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Get statistics menu keyboard."""
    keyboard = [
        [
            InlineKeyboardButton(
                t("stats.mood", lang),
                callback_data="stats_mood"
            ),
            InlineKeyboardButton(
                t("stats.fitness", lang),
                callback_data="stats_fitness"
            ),
        ],
        [
            InlineKeyboardButton(
                t("stats.meditation", lang),
                callback_data="stats_meditation"
            ),
            InlineKeyboardButton(
                t("stats.finance", lang),
                callback_data="stats_finance"
            ),
        ],
        [
            InlineKeyboardButton(
                t("buttons.back", lang),
                callback_data="menu_main"
            ),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_back_to_menu_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Get back to main menu keyboard."""
    keyboard = [
        [
            InlineKeyboardButton(
                t("buttons.back", lang),
                callback_data="menu_main"
            ),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_cancel_keyboard(lang: str = "en") -> ReplyKeyboardMarkup:
    """Get cancel operation keyboard."""
    keyboard = [
        [KeyboardButton(t("buttons.cancel", lang))],
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )
