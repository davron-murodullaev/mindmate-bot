from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Request

from mindmate.api.deps import get_tg_user

router = APIRouter(prefix="/user", tags=["user"])

TgUser = Annotated[dict, Depends(get_tg_user)]


@router.get("/me")
async def get_me(request: Request, tg_user: TgUser):
    user_id: int = tg_user["id"]
    pool = request.app.state.pool

    row = await pool.fetchrow(
        "SELECT user_id, username, first_name, last_name, language_code FROM users WHERE user_id = $1",
        user_id,
    )
    if not row:
        return {
            "user_id": user_id,
            "username": tg_user.get("username"),
            "first_name": tg_user.get("first_name", ""),
            "last_name": tg_user.get("last_name", ""),
            "language_code": "uz",
            "is_premium": False,
        }

    sub = await pool.fetchrow(
        "SELECT tier, expires_at FROM subscriptions WHERE user_id = $1",
        user_id,
    )

    is_premium = False
    if sub and sub["tier"] == "premium":
        expires = sub["expires_at"]
        is_premium = expires is None or expires.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc)

    return {
        "user_id": row["user_id"],
        "username": row["username"],
        "first_name": row["first_name"],
        "last_name": row["last_name"],
        "language_code": row["language_code"],
        "is_premium": is_premium,
    }
