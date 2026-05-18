"""
Handlers module - Telegram bot command and callback handlers.
"""
from mindmate.handlers.start import (
    start_handler,
    language_callback,
    setup_callback,
    cancel_handler,
)
from mindmate.handlers.menu import menu_handler, main_menu_callback
from mindmate.handlers.healer import healer_handler, healer_message_handler
from mindmate.handlers.productivity import productivity_handler, productivity_message_handler
from mindmate.handlers.settings import settings_handler, settings_callback
from mindmate.handlers.premium import premium_handler, premium_callback
from mindmate.handlers.exam import exam_handler, exam_callback, exam_text_handler
from mindmate.handlers.career import career_handler, career_callback, career_text_handler
from mindmate.handlers.profile import profile_handler, profile_callback, profile_action_callback
from mindmate.handlers.friends import (
    friends_handler,
    friends_callback,
    friends_text_handler,
    friends_photo_handler,
)
from mindmate.handlers.legal import privacy_handler, terms_handler, legal_callback
from mindmate.handlers.admin import stats_admin_handler
from mindmate.handlers.payments import (
    buy_premium_handler,
    buy_callback,
    precheckout_handler,
    successful_payment_handler,
)

__all__ = [
    "start_handler",
    "language_callback",
    "setup_callback",
    "cancel_handler",
    "menu_handler",
    "main_menu_callback",
    "healer_handler",
    "healer_message_handler",
    "productivity_handler",
    "productivity_message_handler",
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
    "profile_handler",
    "profile_callback",
    "profile_action_callback",
    "friends_handler",
    "friends_callback",
    "friends_text_handler",
    "friends_photo_handler",
    "privacy_handler",
    "terms_handler",
    "legal_callback",
    "stats_admin_handler",
    "buy_premium_handler",
    "buy_callback",
    "precheckout_handler",
    "successful_payment_handler",
]
