"""
Tool definitions for the AI router.

These are the structured "actions" the AI can choose to perform when a user
sends a free-text or voice message. Each tool maps to a Python coroutine that
actually performs the action and returns a user-facing string.
"""
from typing import List, Dict, Any, Callable, Awaitable, Optional
import logging

from mindmate.db.queries import (
    create_reminder,
    get_user_reminders,
    delete_reminder,
    is_premium_active,
    count_active_reminders,
    get_user,
)
from mindmate.reminders.parser import parse_reminder, format_reminder_time, validate_reminder_time
from mindmate.core.constants import FREE_MAX_REMINDERS

logger = logging.getLogger(__name__)


# OpenAI-compatible tool definitions
TOOLS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "create_reminder",
            "description": (
                "Create a new reminder for the user. Use when user asks to be "
                "reminded of something at a specific time or interval."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Short description of what to remind",
                    },
                    "when": {
                        "type": "string",
                        "description": (
                            "Natural-language time expression in user's words "
                            "(e.g. 'ertaga 15:00', 'tomorrow at 3pm', 'in 2 hours')"
                        ),
                    },
                    "repeat": {
                        "type": "string",
                        "enum": ["once", "daily", "weekly", "monthly"],
                        "description": "How often to repeat (default: once)",
                    },
                },
                "required": ["text", "when"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_reminders",
            "description": "Show the user's active reminders.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_reminder_by_query",
            "description": (
                "Delete reminders that match a query. Use when user asks to "
                "delete/remove/cancel a reminder. If query is 'all' or empty, "
                "deletes every active reminder."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "Substring to match in reminder text, or 'all' to "
                            "delete every active reminder."
                        ),
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "open_menu",
            "description": (
                "Open a specific feature menu when user asks for it by name. "
                "Use this for navigational requests like 'show exam mentor', "
                "'open career coach', 'I want to find friends'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "menu": {
                        "type": "string",
                        "enum": [
                            "main", "exam", "career", "friends", "profile",
                            "healer", "productivity", "settings", "premium",
                        ],
                        "description": "Which menu/feature to open",
                    },
                },
                "required": ["menu"],
            },
        },
    },
]


# ──────────────────────── Tool implementations ────────────────────────

async def tool_create_reminder(
    user_id: int,
    text: str,
    when: str,
    repeat: str = "once",
    lang: str = "uz",
) -> Dict[str, Any]:
    """Create a reminder; returns dict with 'message' for user."""
    if not await is_premium_active(user_id):
        count = await count_active_reminders(user_id)
        if count >= FREE_MAX_REMINDERS:
            return {
                "message": (
                    f"❌ Bepul rejada {FREE_MAX_REMINDERS} ta eslatma chegarasi. "
                    "Premium'ga o'tib cheksiz qiling."
                ),
            }

    user = await get_user(user_id)
    user_tz = (user or {}).get("timezone") or None

    full_text = f"{text} {when}".strip()
    parsed = parse_reminder(full_text, user_timezone=user_tz)
    if not parsed:
        return {
            "message": (
                "❌ Vaqtni tushunmadim. Iltimos, aniqroq ayting "
                "(masalan: \"ertaga soat 15:00 da\")."
            ),
        }

    parsed_text, parsed_time, parsed_repeat = parsed
    repeat_final = repeat if repeat != "once" else parsed_repeat

    if not validate_reminder_time(parsed_time, user_tz):
        return {"message": "❌ Vaqt o'tgan. Kelajakdagi vaqt kerak."}

    await create_reminder(user_id, parsed_text or text, parsed_time, repeat_final)
    return {
        "message": (
            f"✅ Eslatma o'rnatildi:\n"
            f"📌 _{parsed_text or text}_\n"
            f"⏰ {format_reminder_time(parsed_time, user_tz)}"
        ),
    }


async def tool_list_reminders(user_id: int, lang: str = "uz") -> Dict[str, Any]:
    """List user's active reminders."""
    user = await get_user(user_id)
    user_tz = (user or {}).get("timezone") or None
    reminders = await get_user_reminders(user_id, include_sent=False)
    if not reminders:
        return {"message": "📭 Sizda faol eslatmalar yo'q."}

    lines = ["📋 *Sizning eslatmalaringiz:*\n"]
    for r in reminders[:10]:
        lines.append(
            f"• {format_reminder_time(r['reminder_time'], user_tz)} — _{r['text']}_"
        )
    if len(reminders) > 10:
        lines.append(f"\n_va yana {len(reminders) - 10} ta..._")
    lines.append("\n_O'chirish uchun: \"X eslatmani o'chir\" deb yozing._")
    return {"message": "\n".join(lines)}


async def tool_delete_reminder_by_query(
    user_id: int, query: str, lang: str = "uz"
) -> Dict[str, Any]:
    """Delete reminders matching a query, or all if query is 'all'."""
    reminders = await get_user_reminders(user_id, include_sent=False)
    if not reminders:
        return {"message": "📭 O'chirish uchun eslatma yo'q."}

    q = (query or "").strip().lower()
    deleted = 0

    if q in ("all", "hammasi", "barchasi", "все"):
        for r in reminders:
            await delete_reminder(r["id"], user_id)
            deleted += 1
        return {"message": f"🗑 {deleted} ta eslatma o'chirildi."}

    matched = [r for r in reminders if q in r["text"].lower()]
    if not matched:
        return {
            "message": (
                f"🔍 \"{query}\" so'roviga mos eslatma topilmadi.\n\n"
                "Faol eslatmalar ro'yxatini ko'rish uchun: "
                "\"eslatmalarimni ko'rsat\" deb yozing."
            ),
        }

    for r in matched:
        await delete_reminder(r["id"], user_id)
        deleted += 1
    titles = ", ".join(f"_{r['text'][:30]}_" for r in matched[:3])
    return {"message": f"🗑 {deleted} ta eslatma o'chirildi: {titles}"}


async def tool_open_menu(
    user_id: int, menu: str, lang: str = "uz"
) -> Dict[str, Any]:
    """Signal handler to open a specific menu (handled by caller)."""
    return {"open_menu": menu, "message": ""}


# ──────────────────────── Tool registry ────────────────────────

TOOL_FUNCTIONS: Dict[str, Callable[..., Awaitable[Dict[str, Any]]]] = {
    "create_reminder": tool_create_reminder,
    "list_reminders": tool_list_reminders,
    "delete_reminder_by_query": tool_delete_reminder_by_query,
    "open_menu": tool_open_menu,
}
