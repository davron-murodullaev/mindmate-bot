from datetime import date, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Request

from mindmate.api.deps import get_tg_user

router = APIRouter(prefix="/stats", tags=["stats"])

TgUser = Annotated[dict, Depends(get_tg_user)]


@router.get("/overview")
async def get_overview(request: Request, tg_user: TgUser):
    user_id: int = tg_user["id"]
    pool = request.app.state.pool
    today = date.today()

    usage_row = await pool.fetchrow(
        "SELECT ai_messages FROM daily_usage WHERE user_id = $1 AND usage_date = $2",
        user_id, today,
    )
    ai_today = int(usage_row["ai_messages"]) if usage_row else 0

    rows = await pool.fetch(
        """SELECT usage_date FROM daily_usage
           WHERE user_id = $1 AND ai_messages > 0 AND usage_date >= $2
           ORDER BY usage_date DESC""",
        user_id, today - timedelta(days=30),
    )
    active_dates = {r["usage_date"] for r in rows}

    streak = 0
    check = today
    while check in active_dates:
        streak += 1
        check -= timedelta(days=1)

    # Last 7 days (oldest first) — True if user was active that day
    streak_history = [
        (today - timedelta(days=6 - i)) in active_dates
        for i in range(7)
    ]

    return {
        "ai_messages_today": ai_today,
        "streak_days": streak,
        "streak_history": streak_history,
    }
