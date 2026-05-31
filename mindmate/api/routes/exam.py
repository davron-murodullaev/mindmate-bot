from typing import Annotated

from fastapi import APIRouter, Depends, Request

from mindmate.api.deps import get_tg_user

router = APIRouter(prefix="/exam", tags=["exam"])

TgUser = Annotated[dict, Depends(get_tg_user)]


@router.get("/profile")
async def get_exam_profile(request: Request, tg_user: TgUser):
    pool = request.app.state.pool
    row = await pool.fetchrow(
        "SELECT * FROM exam_profiles WHERE user_id = $1",
        tg_user["id"],
    )
    if not row:
        return {}

    result = dict(row)
    if result.get("exam_date"):
        result["exam_date"] = result["exam_date"].isoformat()
    if result.get("updated_at"):
        result["updated_at"] = result["updated_at"].isoformat()
    if result.get("created_at"):
        result["created_at"] = result["created_at"].isoformat()
    result["subjects"] = list(result.get("subjects") or [])
    return result
