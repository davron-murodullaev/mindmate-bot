"""Handler for the /app command — opens the MindMate Mini App."""
import logging
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


def _app_url() -> str:
    base = (
        os.getenv("WEBAPP_URL")
        or os.getenv("RAILWAY_STATIC_URL")
        or os.getenv("APP_URL")
        or ""
    ).rstrip("/")
    return f"{base}/frontend/mindmate-app.html"


async def miniapp_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = _app_url()
    if not url.startswith("https://"):
        await update.message.reply_text(
            "⚠️ Mini App hali sozlanmagan.\n"
            "Railway Variables bo'limiga <code>WEBAPP_URL</code> qo'shing.",
            parse_mode="HTML",
        )
        return

    keyboard = [[
        InlineKeyboardButton(
            text="📱 MindMate ilovasini ochish",
            web_app=WebAppInfo(url=url),
        )
    ]]
    await update.message.reply_text(
        "👇 Quyidagi tugmani bosib MindMate ilovasini oching:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
