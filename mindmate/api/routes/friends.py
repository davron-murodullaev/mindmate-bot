from typing import Annotated

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from mindmate.api.deps import get_tg_user

router = APIRouter(prefix="/friends", tags=["friends"])

TgUser = Annotated[dict, Depends(get_tg_user)]

FREE_DAILY_LIKES = 5


def _serialize_profile(row) -> dict:
    result = dict(row)
    result["interests"] = list(result.get("interests") or [])
    result["photo_file_ids"] = list(result.get("photo_file_ids") or [])
    for key in ("updated_at", "created_at"):
        if result.get(key):
            result[key] = result[key].isoformat()
    return result


@router.get("/profile")
async def get_own_profile(request: Request, tg_user: TgUser):
    pool = request.app.state.pool
    row = await pool.fetchrow(
        "SELECT * FROM friend_profiles WHERE user_id = $1",
        tg_user["id"],
    )
    if not row:
        return {}

    result = _serialize_profile(row)
    likes_count = await pool.fetchval(
        "SELECT COUNT(*) FROM friend_likes WHERE to_user_id = $1 AND is_like = TRUE",
        tg_user["id"],
    )
    result["likes_received"] = int(likes_count or 0)
    return result


@router.get("/browse")
async def browse_next(request: Request, tg_user: TgUser):
    user_id: int = tg_user["id"]
    pool = request.app.state.pool

    prefs = await pool.fetchrow(
        "SELECT * FROM friend_preferences WHERE user_id = $1", user_id
    )
    own = await pool.fetchrow(
        "SELECT city FROM friend_profiles WHERE user_id = $1", user_id
    )

    conditions = [
        "fp.user_id != $1",
        "fp.is_active = TRUE",
        "fp.user_id NOT IN (SELECT to_user_id FROM friend_likes WHERE from_user_id = $1)",
        "fp.user_id NOT IN (SELECT blocked_user_id FROM friend_blocks WHERE user_id = $1)",
        "fp.user_id NOT IN (SELECT user_id FROM friend_blocks WHERE blocked_user_id = $1)",
    ]
    params: list = [user_id]
    idx = 2

    if prefs:
        if prefs["target_gender"]:
            conditions.append(f"fp.gender = ${idx}")
            params.append(prefs["target_gender"])
            idx += 1
        if prefs["min_age"]:
            conditions.append(f"fp.age >= ${idx}")
            params.append(int(prefs["min_age"]))
            idx += 1
        if prefs["max_age"]:
            conditions.append(f"fp.age <= ${idx}")
            params.append(int(prefs["max_age"]))
            idx += 1
        if prefs["same_city_only"] and own and own["city"]:
            conditions.append(f"fp.city = ${idx}")
            params.append(own["city"])
            idx += 1

    where = " AND ".join(conditions)
    row = await pool.fetchrow(
        f"""SELECT fp.user_id, fp.display_name, fp.age, fp.gender, fp.city,
                   fp.interests, fp.looking_for, fp.bio, fp.photo_file_ids
            FROM friend_profiles fp
            WHERE {where}
            ORDER BY RANDOM()
            LIMIT 1""",
        *params,
    )
    if not row:
        return {}

    result = _serialize_profile(row)
    return result


class ReactBody(BaseModel):
    to_user_id: int
    action: str  # "like" | "pass"


@router.post("/react")
async def react(body: ReactBody, request: Request, tg_user: TgUser):
    user_id: int = tg_user["id"]
    pool = request.app.state.pool
    is_like = body.action == "like"

    await pool.execute(
        """INSERT INTO friend_likes (from_user_id, to_user_id, is_like)
           VALUES ($1, $2, $3)
           ON CONFLICT (from_user_id, to_user_id)
           DO UPDATE SET is_like = EXCLUDED.is_like""",
        user_id, body.to_user_id, is_like,
    )

    matched = False
    if is_like:
        mutual = await pool.fetchval(
            "SELECT is_like FROM friend_likes WHERE from_user_id = $1 AND to_user_id = $2",
            body.to_user_id, user_id,
        )
        if mutual:
            u1, u2 = min(user_id, body.to_user_id), max(user_id, body.to_user_id)
            await pool.execute(
                """INSERT INTO friend_matches (user1_id, user2_id)
                   VALUES ($1, $2) ON CONFLICT DO NOTHING""",
                u1, u2,
            )
            matched = True

    return {"success": True, "matched": matched}


@router.get("/matches")
async def get_matches(request: Request, tg_user: TgUser):
    user_id: int = tg_user["id"]
    pool = request.app.state.pool

    rows = await pool.fetch(
        """SELECT fp.user_id, fp.display_name, fp.age, fp.gender, fp.city,
                  fm.matched_at
           FROM friend_matches fm
           JOIN friend_profiles fp ON (
               CASE WHEN fm.user1_id = $1 THEN fm.user2_id ELSE fm.user1_id END = fp.user_id
           )
           WHERE fm.user1_id = $1 OR fm.user2_id = $1
           ORDER BY fm.matched_at DESC
           LIMIT 20""",
        user_id,
    )

    matches = []
    for r in rows:
        m = dict(r)
        if m.get("matched_at"):
            m["matched_at"] = m["matched_at"].isoformat()
        matches.append(m)

    return {"matches": matches}
