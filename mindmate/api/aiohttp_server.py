"""aiohttp web server — runs in the same asyncio event loop as PTB.

Started via AppRunner in post_init; stopped in post_stop.
"""
import json
import logging
import os
import time
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from aiohttp import web

from mindmate.api.auth import validate_telegram_init_data
from mindmate.core.config import settings
from mindmate.db.connection import get_pool

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_WEBAPP_DIR = _PROJECT_ROOT / "webapp"
_INDEX_HTML = _WEBAPP_DIR / "index.html"
_FRONTEND_DIR = _PROJECT_ROOT / "frontend"

_runner: "web.AppRunner | None" = None
_ptb_app = None  # set via register_ptb_app() before web server starts

# Origins allowed to make cross-origin requests to the API.
# Telegram web clients + our own deployed URL.
_WEBAPP_URL = os.getenv("WEBAPP_URL", "").rstrip("/")
ALLOWED_ORIGINS: set[str] = {
    "https://web.telegram.org",
    "https://k.web.telegram.org",
    "https://z.web.telegram.org",
    "https://a.web.telegram.org",
}
if _WEBAPP_URL:
    ALLOWED_ORIGINS.add(_WEBAPP_URL)

# In-memory rate limiter: {ip: [timestamp, ...]}
_rate_store: dict[str, list[float]] = defaultdict(list)

RATE_LIMIT = 30    # max requests
RATE_WINDOW = 60   # per N seconds


def register_ptb_app(app) -> None:
    """Store PTB Application so the webhook handler can push updates to it."""
    global _ptb_app
    _ptb_app = app


# ── Helpers ────────────────────────────────────────────────────────────────

class _Encoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "isoformat"):
            return obj.isoformat()
        return super().default(obj)


def _json(data, status: int = 200) -> web.Response:
    return web.Response(
        text=json.dumps(data, cls=_Encoder),
        content_type="application/json",
        status=status,
    )


def _err(status: int, message: str) -> web.Response:
    return _json({"error": message}, status=status)


async def _auth(request: web.Request) -> "dict | None":
    init_data = request.headers.get("X-Telegram-Init-Data")
    if not init_data:
        return None
    # validate_telegram_init_data now returns the user dict directly (or None)
    return validate_telegram_init_data(init_data, settings.TELEGRAM_BOT_TOKEN)


# ── CORS middleware ────────────────────────────────────────────────────────

@web.middleware
async def cors_middleware(request: web.Request, handler) -> web.Response:
    origin = request.headers.get("Origin", "")
    cors_headers: dict[str, str] = {}
    if origin in ALLOWED_ORIGINS:
        cors_headers = {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, X-Telegram-Init-Data",
            "Vary": "Origin",
        }

    if request.method == "OPTIONS":
        if cors_headers:
            cors_headers["Access-Control-Max-Age"] = "86400"
            return web.Response(status=204, headers=cors_headers)
        return web.Response(status=403)

    response = await handler(request)
    response.headers.update(cors_headers)
    return response


# ── Rate-limit middleware ──────────────────────────────────────────────────

@web.middleware
async def rate_limit_middleware(request: web.Request, handler) -> web.Response:
    if request.path in ("/api/health", "/"):
        return await handler(request)

    ip = request.headers.get("X-Forwarded-For", request.remote or "unknown").split(",")[0].strip()
    now = time.monotonic()
    window_start = now - RATE_WINDOW
    timestamps = _rate_store[ip]

    # Purge expired entries in-place
    while timestamps and timestamps[0] < window_start:
        timestamps.pop(0)

    if len(timestamps) >= RATE_LIMIT:
        logger.warning("Rate limit hit: ip=%s count=%d", ip, len(timestamps))
        return web.json_response(
            {"error": "Juda ko'p so'rov. Biroz kuting."},
            status=429,
            headers={"Retry-After": str(RATE_WINDOW)},
        )

    timestamps.append(now)
    return await handler(request)


# ── Route handlers ─────────────────────────────────────────────────────────

def get_server_port() -> int:
    """Return the port to bind. $PORT (Railway/Render) takes priority."""
    return int(os.environ.get("PORT") or os.environ.get("API_PORT") or settings.API_PORT)


async def health(request: web.Request) -> web.Response:
    checks: dict = {"status": "ok", "db": "unknown"}
    http_status = 200
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        checks["db"] = "ok"
    except Exception:
        logger.exception("Health check: DB error")
        checks["db"] = "error"
        checks["status"] = "degraded"
        http_status = 503
    return _json(checks, status=http_status)


async def get_config(request: web.Request) -> web.Response:
    return _json({"bot_username": settings.BOT_USERNAME})


async def get_user_me(request: web.Request) -> web.Response:
    tg_user = await _auth(request)
    if not tg_user:
        return _err(401, "Unauthorized")

    user_id: int = tg_user["id"]
    pool = await get_pool()

    row = await pool.fetchrow(
        "SELECT user_id, username, first_name, last_name, language_code "
        "FROM users WHERE user_id = $1",
        user_id,
    )
    if not row:
        return _json({
            "user_id": user_id,
            "username": tg_user.get("username"),
            "first_name": tg_user.get("first_name", ""),
            "last_name": tg_user.get("last_name", ""),
            "language_code": "uz",
            "is_premium": False,
        })

    sub = await pool.fetchrow(
        "SELECT tier, expires_at FROM subscriptions WHERE user_id = $1",
        user_id,
    )
    is_premium = False
    if sub and sub["tier"] == "premium":
        expires = sub["expires_at"]
        is_premium = expires is None or expires.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc)

    return _json({
        "user_id": row["user_id"],
        "username": row["username"],
        "first_name": row["first_name"],
        "last_name": row["last_name"],
        "language_code": row["language_code"],
        "is_premium": is_premium,
    })


async def get_exam_profile(request: web.Request) -> web.Response:
    tg_user = await _auth(request)
    if not tg_user:
        return _err(401, "Unauthorized")

    pool = await get_pool()
    row = await pool.fetchrow(
        "SELECT * FROM exam_profiles WHERE user_id = $1",
        tg_user["id"],
    )
    if not row:
        return _json({})

    result = dict(row)
    for key in ("exam_date", "updated_at", "created_at"):
        if result.get(key):
            result[key] = result[key].isoformat()
    result["subjects"] = list(result.get("subjects") or [])
    return _json(result)


async def get_career_profile(request: web.Request) -> web.Response:
    tg_user = await _auth(request)
    if not tg_user:
        return _err(401, "Unauthorized")

    pool = await get_pool()
    row = await pool.fetchrow(
        "SELECT * FROM career_profiles WHERE user_id = $1",
        tg_user["id"],
    )
    if not row:
        return _json({})

    result = dict(row)
    result["skills"] = list(result.get("skills") or [])
    result["languages"] = list(result.get("languages") or [])
    for key in ("updated_at", "created_at"):
        if result.get(key):
            result[key] = result[key].isoformat()
    result.pop("resume_text", None)
    return _json(result)


def _serialize_friend(row) -> dict:
    result = dict(row)
    result["interests"] = list(result.get("interests") or [])
    result["photo_file_ids"] = list(result.get("photo_file_ids") or [])
    for key in ("updated_at", "created_at", "matched_at"):
        if result.get(key):
            result[key] = result[key].isoformat()
    return result


async def get_friends_profile(request: web.Request) -> web.Response:
    tg_user = await _auth(request)
    if not tg_user:
        return _err(401, "Unauthorized")

    pool = await get_pool()
    row = await pool.fetchrow(
        "SELECT * FROM friend_profiles WHERE user_id = $1",
        tg_user["id"],
    )
    if not row:
        return _json({})

    result = _serialize_friend(row)
    likes_count = await pool.fetchval(
        "SELECT COUNT(*) FROM friend_likes WHERE to_user_id = $1 AND is_like = TRUE",
        tg_user["id"],
    )
    result["likes_received"] = int(likes_count or 0)
    return _json(result)


async def browse_friends(request: web.Request) -> web.Response:
    tg_user = await _auth(request)
    if not tg_user:
        return _err(401, "Unauthorized")

    user_id: int = tg_user["id"]
    pool = await get_pool()

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
        return _json({})
    return _json(_serialize_friend(row))


async def react_friends(request: web.Request) -> web.Response:
    tg_user = await _auth(request)
    if not tg_user:
        return _err(401, "Unauthorized")

    try:
        body = await request.json()
    except Exception:
        return _err(400, "Invalid JSON")

    user_id: int = tg_user["id"]
    to_user_id = body.get("to_user_id")
    action = body.get("action")
    if not to_user_id or action not in ("like", "pass"):
        return _err(400, "Invalid parameters")

    pool = await get_pool()
    is_like = action == "like"

    await pool.execute(
        """INSERT INTO friend_likes (from_user_id, to_user_id, is_like)
           VALUES ($1, $2, $3)
           ON CONFLICT (from_user_id, to_user_id)
           DO UPDATE SET is_like = EXCLUDED.is_like""",
        user_id, to_user_id, is_like,
    )

    matched = False
    if is_like:
        mutual = await pool.fetchval(
            "SELECT is_like FROM friend_likes WHERE from_user_id = $1 AND to_user_id = $2",
            to_user_id, user_id,
        )
        if mutual:
            u1, u2 = min(user_id, to_user_id), max(user_id, to_user_id)
            await pool.execute(
                """INSERT INTO friend_matches (user1_id, user2_id)
                   VALUES ($1, $2) ON CONFLICT DO NOTHING""",
                u1, u2,
            )
            matched = True

    return _json({"success": True, "matched": matched})


async def get_matches(request: web.Request) -> web.Response:
    tg_user = await _auth(request)
    if not tg_user:
        return _err(401, "Unauthorized")

    user_id: int = tg_user["id"]
    pool = await get_pool()

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
    return _json({"matches": [_serialize_friend(r) for r in rows]})


async def get_stats_overview(request: web.Request) -> web.Response:
    tg_user = await _auth(request)
    if not tg_user:
        return _err(401, "Unauthorized")

    user_id: int = tg_user["id"]
    pool = await get_pool()
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

    streak_history = [
        (today - timedelta(days=6 - i)) in active_dates
        for i in range(7)
    ]

    return _json({
        "ai_messages_today": ai_today,
        "streak_days": streak,
        "streak_history": streak_history,
    })


# ── Telegram Webhook ────────────────────────────────────────────────────────

async def telegram_webhook(request: web.Request) -> web.Response:
    """Receive Telegram updates via POST and push them to PTB's update queue."""
    from telegram import Update

    secret = request.match_info.get("secret", "")
    expected = settings.TELEGRAM_BOT_TOKEN.replace(":", "_")
    if secret != expected:
        return web.Response(status=403)
    if _ptb_app is None:
        return web.Response(text="not ready", status=503)
    try:
        data = await request.json()
        update = Update.de_json(data, _ptb_app.bot)
        await _ptb_app.update_queue.put(update)
        return web.Response(text="ok")
    except Exception as e:
        logger.error("Webhook handler error: %s", e)
        return web.Response(status=500)


# ── Static / SPA serving ────────────────────────────────────────────────────

async def serve_frontend(request: web.Request) -> web.Response:
    filename = request.match_info.get("filename", "mindmate-app.html")
    try:
        target = (_FRONTEND_DIR / filename).resolve()
        target.relative_to(_FRONTEND_DIR.resolve())
    except ValueError:
        raise web.HTTPNotFound()
    if target.is_file():
        return web.FileResponse(str(target))
    raise web.HTTPNotFound()


async def serve_index(request: web.Request) -> web.Response:
    if _INDEX_HTML.is_file():
        return web.FileResponse(str(_INDEX_HTML))
    return web.Response(
        text="<h2>MindMate API is running ✓</h2>",
        content_type="text/html",
    )


async def serve_spa(request: web.Request) -> web.Response:
    path = request.match_info.get("path", "")
    if path.startswith("api/"):
        raise web.HTTPNotFound()
    # Prevent path traversal
    try:
        target = (_WEBAPP_DIR / path).resolve()
        target.relative_to(_WEBAPP_DIR.resolve())
    except ValueError:
        raise web.HTTPNotFound()
    if target.is_file():
        return web.FileResponse(str(target))
    if _INDEX_HTML.is_file():
        return web.FileResponse(str(_INDEX_HTML))
    return web.Response(
        text="<h2>MindMate API is running ✓</h2>",
        content_type="text/html",
    )


# ── App factory ────────────────────────────────────────────────────────────

def _create_app() -> web.Application:
    app = web.Application(middlewares=[cors_middleware, rate_limit_middleware])

    app.router.add_post("/telegram/webhook/{secret}", telegram_webhook)
    app.router.add_get("/api/health", health)
    app.router.add_get("/api/config", get_config)
    app.router.add_get("/api/user/me", get_user_me)
    app.router.add_get("/api/exam/profile", get_exam_profile)
    app.router.add_get("/api/career/profile", get_career_profile)
    app.router.add_get("/api/friends/profile", get_friends_profile)
    app.router.add_get("/api/friends/browse", browse_friends)
    app.router.add_post("/api/friends/react", react_friends)
    app.router.add_get("/api/friends/matches", get_matches)
    app.router.add_get("/api/stats/overview", get_stats_overview)
    app.router.add_get("/frontend/{filename}", serve_frontend)
    app.router.add_get("/frontend/", serve_frontend)
    app.router.add_get("/", serve_index)
    app.router.add_get("/{path:.*}", serve_spa)

    return app


# ── Lifecycle ──────────────────────────────────────────────────────────────

async def start_web_server() -> None:
    global _runner
    port = get_server_port()
    app = _create_app()
    _runner = web.AppRunner(app)
    await _runner.setup()
    site = web.TCPSite(_runner, "0.0.0.0", port)
    await site.start()
    logger.info("HTTP server started on port %d", port)


async def stop_web_server() -> None:
    global _runner
    if _runner:
        await _runner.cleanup()
        _runner = None
        logger.info("Mini App web server stopped")
