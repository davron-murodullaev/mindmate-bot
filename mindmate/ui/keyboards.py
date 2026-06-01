"""
Keyboard builders for MindMate Bot
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

from mindmate.i18n import t


def get_language_keyboard() -> InlineKeyboardMarkup:
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
    keyboard = [
        [InlineKeyboardButton(t("buttons.confirm", lang), callback_data="setup_complete")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_main_menu_keyboard(lang: str = "en", webapp_url: str = "") -> InlineKeyboardMarkup:
    """Main menu — 4 big categories + optional Mini App button."""
    keyboard = [
        [
            InlineKeyboardButton(t("menu.exam", lang), callback_data="menu_exam"),
            InlineKeyboardButton(t("menu.career", lang), callback_data="menu_career"),
        ],
        [
            InlineKeyboardButton(t("menu.friends", lang), callback_data="menu_friends"),
            InlineKeyboardButton(t("menu.profile", lang), callback_data="menu_profile"),
        ],
    ]
    if webapp_url:
        keyboard.append([
            InlineKeyboardButton("📱 Open Dashboard", web_app=WebAppInfo(url=webapp_url))
        ])
    return InlineKeyboardMarkup(keyboard)


def get_profile_menu_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Profile sub-menu."""
    keyboard = [
        [
            InlineKeyboardButton(t("menu.healer", lang), callback_data="menu_healer"),
            InlineKeyboardButton(t("menu.productivity", lang), callback_data="menu_productivity"),
        ],
        [
            InlineKeyboardButton(t("menu.settings", lang), callback_data="menu_settings"),
            InlineKeyboardButton(t("menu.premium", lang), callback_data="menu_premium"),
        ],
        [
            InlineKeyboardButton(t("buttons.back", lang), callback_data="menu_main"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_settings_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(t("settings.language", lang), callback_data="settings_language")],
        [InlineKeyboardButton(t("settings.timezone", lang), callback_data="settings_timezone")],
        [InlineKeyboardButton(t("settings.delete_data", lang), callback_data="settings_delete")],
        [InlineKeyboardButton(t("buttons.back", lang), callback_data="menu_profile")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_premium_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(t("premium.subscribe_stars", lang), callback_data="premium_stars")],
        [InlineKeyboardButton(t("premium.subscribe_card", lang), callback_data="premium_card")],
        [InlineKeyboardButton(t("buttons.back", lang), callback_data="menu_profile")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_back_to_menu_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Generic back to main menu keyboard."""
    keyboard = [
        [InlineKeyboardButton(t("buttons.back", lang), callback_data="menu_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_back_to_profile_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Back to profile keyboard."""
    keyboard = [
        [InlineKeyboardButton(t("buttons.back", lang), callback_data="menu_profile")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_cancel_keyboard(lang: str = "en") -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(t("buttons.cancel", lang))],
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True,
    )
