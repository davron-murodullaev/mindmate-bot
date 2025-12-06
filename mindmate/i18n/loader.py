"""
Internationalization loader and utilities
"""
from typing import Dict, Any, Optional
import logging

from mindmate.i18n import en, ru, uz
from mindmate.core.constants import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES

logger = logging.getLogger(__name__)


class I18n:
    """Internationalization handler."""

    def __init__(self):
        """Initialize i18n with all language modules."""
        self.translations: Dict[str, Dict[str, Any]] = {
            "en": en.TRANSLATIONS,
            "ru": ru.TRANSLATIONS,
            "uz": uz.TRANSLATIONS,
        }
        self.default_language = DEFAULT_LANGUAGE

    def get(self, key: str, language: Optional[str] = None, **kwargs) -> str:
        """
        Get translated text for a key.

        Args:
            key: Translation key (supports dot notation, e.g., 'menu.main_menu')
            language: Language code (defaults to DEFAULT_LANGUAGE)
            **kwargs: Format arguments for the translation string

        Returns:
            Translated and formatted text
        """
        lang = language or self.default_language

        # Fallback to default language if requested language not supported
        if lang not in SUPPORTED_LANGUAGES:
            lang = self.default_language

        # Get translation dictionary for language
        lang_dict = self.translations.get(lang, self.translations[self.default_language])

        # Support dot notation for nested keys
        keys = key.split(".")
        value = lang_dict

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                break

        # If translation not found, try English as fallback
        if value is None and lang != "en":
            lang_dict = self.translations["en"]
            value = lang_dict
            for k in keys:
                if isinstance(value, dict):
                    value = value.get(k)
                else:
                    break

        # If still not found, return the key itself
        if value is None:
            logger.warning(f"Translation not found for key: {key} in language: {lang}")
            return key

        # If value is a dict, it means we haven't reached a leaf node
        if isinstance(value, dict):
            logger.warning(f"Translation key points to a dict, not a string: {key}")
            return key

        # Format the string with provided kwargs
        try:
            return str(value).format(**kwargs) if kwargs else str(value)
        except KeyError as e:
            logger.error(f"Missing format argument for key {key}: {e}")
            return str(value)

    def get_supported_languages(self) -> list:
        """Get list of supported language codes."""
        return SUPPORTED_LANGUAGES

    def is_supported(self, language: str) -> bool:
        """Check if a language is supported."""
        return language in SUPPORTED_LANGUAGES


# Global i18n instance
i18n = I18n()


def t(key: str, language: Optional[str] = None, **kwargs) -> str:
    """
    Shorthand function for getting translations.

    Args:
        key: Translation key
        language: Language code
        **kwargs: Format arguments

    Returns:
        Translated text
    """
    return i18n.get(key, language, **kwargs)
