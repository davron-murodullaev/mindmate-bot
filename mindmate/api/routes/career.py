from typing import Annotated

from fastapi import APIRouter, Depends, Request

from mindmate.api.deps import get_tg_user

router = APIRouter(prefix="/career", tags=["career"])

TgUser = Annotated[dict, Depends(get_tg_user)]


@router.get("/profile")
async def get_career_profile(request: Request, tg_user: TgUser):
    pool = request.app.state.pool
    row = await pool.fetchrow(
        "SELECT * FROM career_profiles WHERE user_id = $1",
        tg_user["id"],
    )
    if not row:
        return {}

    result = dict(row)
    result["skills"] = list(result.get("skills") or [])
    result["languages"] = list(result.get("languages") or [])
    if result.get("updated_at"):
        result["updated_at"] = result["updated_at"].isoformat()
    if result.get("created_at"):
        result["created_at"] = result["created_at"].isoformat()
    result.pop("resume_text", None)  # don't expose full resume in API
    return result
