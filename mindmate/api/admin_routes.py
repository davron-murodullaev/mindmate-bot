"""
Admin REST API — used by the /dashboard/ web panel.

Auth:  POST /api/admin/login  { password } → { token }
       All other routes: Authorization: Bearer <token>
"""
import json
import logging
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Set

from aiohttp import web

from mindmate.db.connection import get_pool

logger = logging.getLogger(__name__)

_valid_tokens: Set[str] = set()
_ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")


class _Enc(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "isoformat"):
            return obj.isoformat()
        return super().default(obj)


def _json(data, status: int = 200) -> web.Response:
    return web.Response(
        text=json.dumps(data, cls=_Enc),
        content_type="application/json",
        status=status,
    )


def _err(status: int, msg: str) -> web.Response:
    return _json({"error": msg}, status=status)


def _require_auth(request: web.Request) -> bool:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return False
    return auth[7:] in _valid_tokens


# ── Auth ─────────────────────────────────────────────────────────────────────

async def admin_login(request: web.Request) -> web.Response:
    if not _ADMIN_PASSWORD:
        return _err(503, "ADMIN_PASSWORD not configured")
    try:
        body = await request.json()
    except Exception:
        return _err(400, "Invalid JSON")
    if not secrets.compare_digest(body.get("password", ""), _ADMIN_PASSWORD):
        return _err(401, "Invalid password")
    token = secrets.token_urlsafe(32)
    _valid_tokens.add(token)
    return _json({"token": token})


# ── Stats ─────────────────────────────────────────────────────────────────────

async def admin_stats(request: web.Request) -> web.Response:
    if not _require_auth(request):
        return _err(401, "Unauthorized")
    pool = await get_pool()
    total_users = await pool.fetchval("SELECT COUNT(*) FROM users")
    active_today = await pool.fetchval(
        "SELECT COUNT(DISTINCT user_id) FROM daily_usage WHERE usage_date = CURRENT_DATE"
    )
    premium_users = await pool.fetchval(
        "SELECT COUNT(*) FROM subscriptions "
        "WHERE tier = 'premium' AND (expires_at IS NULL OR expires_at > NOW())"
    )
    total_messages = await pool.fetchval(
        "SELECT COALESCE(SUM(ai_messages), 0) FROM daily_usage"
    )
    new_today = await pool.fetchval(
        "SELECT COUNT(*) FROM users WHERE created_at >= CURRENT_DATE"
    )
    friend_profiles = await pool.fetchval(
        "SELECT COUNT(*) FROM friend_profiles WHERE is_active = TRUE"
    )
    return _json({
        "total_users": int(total_users or 0),
        "active_today": int(active_today or 0),
        "premium_users": int(premium_users or 0),
        "total_messages": int(total_messages or 0),
        "new_today": int(new_today or 0),
        "friend_profiles": int(friend_profiles or 0),
    })


# ── Users ─────────────────────────────────────────────────────────────────────

async def admin_users(request: web.Request) -> web.Response:
    if not _require_auth(request):
        return _err(401, "Unauthorized")
    pool = await get_pool()
    page = max(1, int(request.rel_url.query.get("page", "1")))
    per_page = min(50, max(5, int(request.rel_url.query.get("per_page", "20"))))
    search = request.rel_url.query.get("search", "").strip()
    offset = (page - 1) * per_page

    base = """
        SELECT u.user_id, u.username, u.first_name, u.last_name,
               u.language_code, u.created_at, u.last_active, u.is_active,
               s.tier AS subscription_tier, s.expires_at
        FROM users u
        LEFT JOIN subscriptions s ON s.user_id = u.user_id
    """
    if search:
        where = (
            " WHERE u.username ILIKE $1 OR u.first_name ILIKE $1"
            " OR u.last_name ILIKE $1 OR CAST(u.user_id AS TEXT) = $2"
        )
        rows = await pool.fetch(
            base + where + " ORDER BY u.created_at DESC LIMIT $3 OFFSET $4",
            f"%{search}%", search, per_page, offset,
        )
        total = await pool.fetchval(
            "SELECT COUNT(*) FROM users u" + where, f"%{search}%", search
        )
    else:
        rows = await pool.fetch(
            base + " ORDER BY u.created_at DESC LIMIT $1 OFFSET $2",
            per_page, offset,
        )
        total = await pool.fetchval("SELECT COUNT(*) FROM users")

    now_iso = datetime.now(timezone.utc).isoformat()
    users = []
    for row in rows:
        u = dict(row)
        for key in ("created_at", "last_active", "expires_at"):
            if u.get(key):
                u[key] = u[key].isoformat()
        tier = u.get("subscription_tier") or "free"
        exp = u.get("expires_at")
        u["is_premium"] = tier == "premium" and (exp is None or str(exp) > now_iso)
        users.append(u)

    return _json({
        "users": users,
        "total": int(total or 0),
        "page": page,
        "per_page": per_page,
        "pages": max(1, -(-int(total or 0) // per_page)),
    })


async def admin_add_premium(request: web.Request) -> web.Response:
    if not _require_auth(request):
        return _err(401, "Unauthorized")
    user_id = int(request.match_info.get("user_id", "0"))
    try:
        body = await request.json()
        days = int(body.get("days", 30))
    except Exception:
        days = 30
    expires_at = datetime.now(timezone.utc) + timedelta(days=days)
    pool = await get_pool()
    await pool.execute(
        """INSERT INTO subscriptions (user_id, tier, expires_at, updated_at)
           VALUES ($1, 'premium', $2, NOW())
           ON CONFLICT (user_id) DO UPDATE
           SET tier = 'premium', expires_at = $2, updated_at = NOW()""",
        user_id, expires_at,
    )
    logger.info("Admin: premium granted user=%d days=%d", user_id, days)
    return _json({"success": True, "expires_at": expires_at.isoformat()})


async def admin_remove_premium(request: web.Request) -> web.Response:
    if not _require_auth(request):
        return _err(401, "Unauthorized")
    user_id = int(request.match_info.get("user_id", "0"))
    pool = await get_pool()
    await pool.execute(
        "UPDATE subscriptions SET tier = 'free', expires_at = NULL, updated_at = NOW() WHERE user_id = $1",
        user_id,
    )
    logger.info("Admin: premium removed user=%d", user_id)
    return _json({"success": True})


async def admin_ban_user(request: web.Request) -> web.Response:
    if not _require_auth(request):
        return _err(401, "Unauthorized")
    user_id = int(request.match_info.get("user_id", "0"))
    pool = await get_pool()
    await pool.execute("UPDATE users SET is_active = FALSE WHERE user_id = $1", user_id)
    logger.info("Admin: banned user=%d", user_id)
    return _json({"success": True})


async def admin_unban_user(request: web.Request) -> web.Response:
    if not _require_auth(request):
        return _err(401, "Unauthorized")
    user_id = int(request.match_info.get("user_id", "0"))
    pool = await get_pool()
    await pool.execute("UPDATE users SET is_active = TRUE WHERE user_id = $1", user_id)
    logger.info("Admin: unbanned user=%d", user_id)
    return _json({"success": True})


# ── Broadcast ─────────────────────────────────────────────────────────────────

async def admin_broadcast(request: web.Request) -> web.Response:
    if not _require_auth(request):
        return _err(401, "Unauthorized")
    try:
        body = await request.json()
    except Exception:
        return _err(400, "Invalid JSON")
    msg_text = body.get("message", "").strip()
    if not msg_text:
        return _err(400, "message is required")
    target = body.get("target", "all")

    pool = await get_pool()
    if target == "premium":
        rows = await pool.fetch(
            """SELECT u.user_id FROM users u
               JOIN subscriptions s ON s.user_id = u.user_id
               WHERE u.is_active = TRUE AND s.tier = 'premium'
                 AND (s.expires_at IS NULL OR s.expires_at > NOW())"""
        )
    else:
        rows = await pool.fetch("SELECT user_id FROM users WHERE is_active = TRUE")

    # Late import to avoid circular dependency at module load time
    from mindmate.api.aiohttp_server import _ptb_app
    if _ptb_app is None:
        return _err(503, "Bot not available")

    sent = failed = 0
    for row in rows:
        try:
            await _ptb_app.bot.send_message(
                chat_id=row["user_id"], text=msg_text, parse_mode="HTML"
            )
            sent += 1
        except Exception as exc:
            logger.warning("Broadcast to %d failed: %s", row["user_id"], exc)
            failed += 1

    logger.info("Broadcast done: target=%s sent=%d failed=%d", target, sent, failed)
    return _json({"success": True, "sent": sent, "failed": failed, "total": sent + failed})


# ── Growth chart ──────────────────────────────────────────────────────────────

async def admin_growth(request: web.Request) -> web.Response:
    if not _require_auth(request):
        return _err(401, "Unauthorized")
    pool = await get_pool()
    rows = await pool.fetch(
        """SELECT DATE(created_at) AS day, COUNT(*) AS new_users
           FROM users
           WHERE created_at >= NOW() - INTERVAL '30 days'
           GROUP BY DATE(created_at)
           ORDER BY day"""
    )
    return _json({"data": [{"date": str(r["day"]), "users": int(r["new_users"])} for r in rows]})


# ── Registration ──────────────────────────────────────────────────────────────

def setup_admin_routes(app: web.Application) -> None:
    """Attach all admin routes to the aiohttp application."""
    app.router.add_post("/api/admin/login", admin_login)
    app.router.add_get("/api/admin/stats", admin_stats)
    app.router.add_get("/api/admin/users", admin_users)
    app.router.add_post("/api/admin/users/{user_id}/premium", admin_add_premium)
    app.router.add_delete("/api/admin/users/{user_id}/premium", admin_remove_premium)
    app.router.add_post("/api/admin/users/{user_id}/ban", admin_ban_user)
    app.router.add_delete("/api/admin/users/{user_id}/ban", admin_unban_user)
    app.router.add_post("/api/admin/broadcast", admin_broadcast)
    app.router.add_get("/api/admin/growth", admin_growth)
