"""
Handlers module - Telegram bot command and callback handlers.
"""
from mindmate.handlers.start import start_handler, language_callback, setup_callback
from mindmate.handlers.menu import menu_handler, main_menu_callback
from mindmate.handlers.mood import mood_handler, mood_callback, save_mood_handler
from mindmate.handlers.healer import healer_handler, healer_message_handler
from mindmate.handlers.journal import journal_handler, journal_callback, save_journal_handler
from mindmate.handlers.productivity import productivity_handler, productivity_message_handler
from mindmate.handlers.stats import stats_handler, stats_callback
from mindmate.handlers.reminders import (
    reminders_handler,
    reminders_callback,
    reminder_text_handler,
)
from mindmate.handlers.settings import settings_handler, settings_callback
from mindmate.handlers.premium import premium_handler, premium_callback
from mindmate.handlers.exam import exam_handler, exam_callback, exam_text_handler
from mindmate.handlers.career import career_handler, career_callback, career_text_handler

__all__ = [
    "start_handler",
    "language_callback",
    "setup_callback",
    "menu_handler",
    "main_menu_callback",
    "mood_handler",
    "mood_callback",
    "save_mood_handler",
    "healer_handler",
    "healer_message_handler",
    "journal_handler",
    "journal_callback",
    "save_journal_handler",
    "productivity_handler",
    "productivity_message_handler",
    "stats_handler",
    "stats_callback",
    "reminders_handler",
    "reminders_callback",
    "reminder_text_handler",
    "settings_handler",
    "settings_callback",
    "premium_handler",
    "premium_callback",
    "exam_handler",
    "exam_callback",
    "exam_text_handler",
    "career_handler",
    "career_callback",
    "career_text_handler",
]
