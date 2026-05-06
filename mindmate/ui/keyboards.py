"""
Keyboard builders for MindMate Bot
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

from mindmate.i18n import t
from mindmate.core.constants import MOOD_EMOJIS


def get_language_keyboard() -> InlineKeyboardMarkup:
    """Get language selection keyboard."""
    keyboard = [
        [
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        ],
        [
            InlineKeyboardButton("🇺🇿 O'zbek", callback_data="lang_uz"),
        ],
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
    """Get main menu keyboard - simplified to core features."""
    keyboard = [
        [
            InlineKeyboardButton(t("menu.healer", lang), callback_data="menu_healer"),
            InlineKeyboardButton(t("menu.productivity", lang), callback_data="menu_productivity"),
        ],
        [
            InlineKeyboardButton(t("menu.mood_tracking", lang), callback_data="menu_mood"),
            InlineKeyboardButton(t("menu.journal", lang), callback_data="menu_journal"),
        ],
        [
            InlineKeyboardButton(t("menu.reminders", lang), callback_data="menu_reminders"),
            InlineKeyboardButton(t("menu.stats", lang), callback_data="menu_stats"),
        ],
        [
            InlineKeyboardButton(t("menu.premium", lang), callback_data="menu_premium"),
            InlineKeyboardButton(t("menu.settings", lang), callback_data="menu_settings"),
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
            InlineKeyboardButton(t("buttons.back", lang), callback_data="menu_main"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_journal_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Get journal menu keyboard."""
    keyboard = [
        [InlineKeyboardButton(t("journal.new_entry", lang), callback_data="journal_new")],
        [InlineKeyboardButton(t("journal.view_entries", lang), callback_data="journal_view")],
        [InlineKeyboardButton(t("buttons.back", lang), callback_data="menu_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_reminders_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Get reminders menu keyboard."""
    keyboard = [
        [InlineKeyboardButton(t("reminders.new", lang), callback_data="reminder_new")],
        [InlineKeyboardButton(t("reminders.list", lang), callback_data="reminder_list")],
        [InlineKeyboardButton(t("buttons.back", lang), callback_data="menu_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_stats_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Get statistics menu keyboard - simplified."""
    keyboard = [
        [
            InlineKeyboardButton(t("stats.mood", lang), callback_data="stats_mood"),
            InlineKeyboardButton(t("stats.journal", lang), callback_data="stats_journal"),
        ],
        [InlineKeyboardButton(t("stats.overall", lang), callback_data="stats_overall")],
        [InlineKeyboardButton(t("buttons.back", lang), callback_data="menu_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_settings_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Get settings menu keyboard."""
    keyboard = [
        [InlineKeyboardButton(t("settings.language", lang), callback_data="settings_language")],
        [InlineKeyboardButton(t("settings.timezone", lang), callback_data="settings_timezone")],
        [InlineKeyboardButton(t("settings.delete_data", lang), callback_data="settings_delete")],
        [InlineKeyboardButton(t("buttons.back", lang), callback_data="menu_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_premium_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Get premium subscription keyboard."""
    keyboard = [
        [InlineKeyboardButton(t("premium.subscribe_stars", lang), callback_data="premium_stars")],
        [InlineKeyboardButton(t("premium.subscribe_card", lang), callback_data="premium_card")],
        [InlineKeyboardButton(t("buttons.back", lang), callback_data="menu_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_back_to_menu_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Get back to main menu keyboard."""
    keyboard = [
        [InlineKeyboardButton(t("buttons.back", lang), callback_data="menu_main")],
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
        one_time_keyboard=True,
    )
