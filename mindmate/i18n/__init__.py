"""
i18n - Internationalization module for MindMate

This module provides multi-language support for the MindMate bot.
Supports 13 languages: UZ, RU, EN, TR, AR, HI, ZH, KO, JA, ES, FR, DE, PT
"""

from .loader import get_text, get_mood_response, get_language_keyboard, SUPPORTED_LANGUAGES

__all__ = [
    'get_text',
    'get_mood_response',
    'get_language_keyboard',
    'SUPPORTED_LANGUAGES',
]
