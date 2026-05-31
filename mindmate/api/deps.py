"""Shared FastAPI dependencies."""
from typing import Annotated, Optional
from fastapi import Header, HTTPException, Request

from mindmate.api.auth import validate_telegram_init_data
from mindmate.core.config import settings


async def get_tg_user(
    request: Request,
    x_telegram_init_data: Annotated[Optional[str], Header()] = None,
) -> dict:
    """Dependency: validate Telegram initData and return the user dict."""
    if not x_telegram_init_data:
        raise HTTPException(status_code=401, detail="Missing X-Telegram-Init-Data header")

    data = validate_telegram_init_data(x_telegram_init_data, settings.TELEGRAM_BOT_TOKEN)
    if not data or "user" not in data:
        raise HTTPException(status_code=401, detail="Invalid Telegram initData")

    return data["user"]
