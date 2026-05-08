"""
Database queries for MindMate Bot
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import logging

from mindmate.db.connection import execute_query, execute_fetchrow, execute_fetchval

logger = logging.getLogger(__name__)


# ──────────────────────── User Queries ────────────────────────

async def create_user(
    user_id: int,
    username: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    language_code: str = "en",
) -> None:
    """Create a new user or update existing one."""
    query = """
        INSERT INTO users (user_id, username, first_name, last_name, language_code)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (user_id) DO UPDATE
        SET username = EXCLUDED.username,
            first_name = EXCLUDED.first_name,
            last_name = EXCLUDED.last_name,
            last_active = CURRENT_TIMESTAMP
    """
    await execute_query(query, user_id, username, first_name, last_name, language_code)


async def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user by ID."""
    query = "SELECT * FROM users WHERE user_id = $1"
    row = await execute_fetchrow(query, user_id)
    return dict(row) if row else None


async def update_user_language(user_id: int, language_code: str) -> None:
    """Update user's language preference."""
    query = "UPDATE users SET language_code = $1 WHERE user_id = $2"
    await execute_query(query, language_code, user_id)


async def update_user_timezone(user_id: int, timezone: str) -> None:
    """Update user's timezone."""
    query = "UPDATE users SET timezone = $1 WHERE user_id = $2"
    await execute_query(query, timezone, user_id)


async def delete_user_data(user_id: int) -> None:
    """Delete all user-related data (CASCADE handles related tables)."""
    query = "DELETE FROM users WHERE user_id = $1"
    await execute_query(query, user_id)


# ──────────────────────── Mood Queries ────────────────────────

async def create_mood(
    user_id: int,
    mood_type: str,
    intensity: int = 5,
    notes: Optional[str] = None,
) -> int:
    """Create a new mood entry."""
    query = """
        INSERT INTO moods (user_id, mood_type, intensity, notes)
        VALUES ($1, $2, $3, $4)
        RETURNING id
    """
    return await execute_fetchval(query, user_id, mood_type, intensity, notes)


async def get_user_moods(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """Get user's recent moods."""
    query = """
        SELECT * FROM moods
        WHERE user_id = $1
        ORDER BY created_at DESC
        LIMIT $2
    """
    rows = await execute_query(query, user_id, limit, fetch=True)
    return [dict(row) for row in rows]


async def get_mood_stats(user_id: int, days: int = 7) -> Dict[str, int]:
    """Get mood statistics for the past N days (parameterized — safe)."""
    query = """
        SELECT mood_type, COUNT(*) AS count
        FROM moods
        WHERE user_id = $1
          AND created_at >= NOW() - ($2::int * INTERVAL '1 day')
        GROUP BY mood_type
    """
    rows = await execute_query(query, user_id, days, fetch=True)
    return {row["mood_type"]: row["count"] for row in rows}


# ──────────────────────── Journal Queries ────────────────────────

async def create_journal(
    user_id: int,
    content: str,
    mood: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> int:
    """Create a new journal entry."""
    query = """
        INSERT INTO journals (user_id, content, mood, tags)
        VALUES ($1, $2, $3, $4)
        RETURNING id
    """
    return await execute_fetchval(query, user_id, content, mood, tags or [])


async def get_user_journals(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """Get user's recent journal entries."""
    query = """
        SELECT * FROM journals
        WHERE user_id = $1
        ORDER BY created_at DESC
        LIMIT $2
    """
    rows = await execute_query(query, user_id, limit, fetch=True)
    return [dict(row) for row in rows]


async def count_user_journals(user_id: int, days: int = 7) -> int:
    """Count user's journal entries in the past N days."""
    query = """
        SELECT COUNT(*) FROM journals
        WHERE user_id = $1
          AND created_at >= NOW() - ($2::int * INTERVAL '1 day')
    """
    return await execute_fetchval(query, user_id, days) or 0


# ──────────────────────── Reminder Queries ────────────────────────

async def create_reminder(
    user_id: int,
    text: str,
    reminder_time: datetime,
    repeat_type: str = "once",
) -> int:
    """Create a new reminder."""
    query = """
        INSERT INTO reminders (user_id, text, reminder_time, repeat_type)
        VALUES ($1, $2, $3, $4)
        RETURNING id
    """
    return await execute_fetchval(query, user_id, text, reminder_time, repeat_type)


async def get_pending_reminders(current_time: datetime) -> List[Dict[str, Any]]:
    """Get all pending reminders due before current_time."""
    query = """
        SELECT * FROM reminders
        WHERE is_sent = false AND reminder_time <= $1
        ORDER BY reminder_time
    """
    rows = await execute_query(query, current_time, fetch=True)
    return [dict(row) for row in rows]


async def mark_reminder_sent(reminder_id: int) -> None:
    """Mark a reminder as sent."""
    query = "UPDATE reminders SET is_sent = true WHERE id = $1"
    await execute_query(query, reminder_id)


async def update_reminder_time(reminder_id: int, new_time: datetime) -> None:
    """Reschedule a reminder to a new time and mark it not-sent."""
    query = """
        UPDATE reminders
        SET reminder_time = $1, is_sent = false
        WHERE id = $2
    """
    await execute_query(query, new_time, reminder_id)


async def get_user_reminders(
    user_id: int, include_sent: bool = False
) -> List[Dict[str, Any]]:
    """Get user's reminders."""
    if include_sent:
        query = """
            SELECT * FROM reminders
            WHERE user_id = $1
            ORDER BY reminder_time DESC
            LIMIT 20
        """
    else:
        query = """
            SELECT * FROM reminders
            WHERE user_id = $1 AND is_sent = false
            ORDER BY reminder_time
        """
    rows = await execute_query(query, user_id, fetch=True)
    return [dict(row) for row in rows]


async def count_active_reminders(user_id: int) -> int:
    """Count user's active (not yet sent) reminders."""
    query = """
        SELECT COUNT(*) FROM reminders
        WHERE user_id = $1 AND is_sent = false
    """
    return await execute_fetchval(query, user_id) or 0


async def delete_reminder(reminder_id: int, user_id: int) -> None:
    """Delete a reminder (scoped to user_id for safety)."""
    query = "DELETE FROM reminders WHERE id = $1 AND user_id = $2"
    await execute_query(query, reminder_id, user_id)


# ──────────────────────── Conversation Queries ────────────────────────

async def save_conversation_message(
    user_id: int, mode: str, role: str, content: str
) -> None:
    """Save a conversation message."""
    query = """
        INSERT INTO conversations (user_id, mode, role, content)
        VALUES ($1, $2, $3, $4)
    """
    await execute_query(query, user_id, mode, role, content)


async def get_conversation_history(
    user_id: int, mode: str, limit: int = 20
) -> List[Dict[str, Any]]:
    """Get conversation history (chronological order)."""
    query = """
        SELECT * FROM conversations
        WHERE user_id = $1 AND mode = $2
        ORDER BY created_at DESC
        LIMIT $3
    """
    rows = await execute_query(query, user_id, mode, limit, fetch=True)
    return [dict(row) for row in reversed(rows)]


async def clear_conversation_history(user_id: int, mode: str) -> None:
    """Clear conversation history for a specific mode."""
    query = "DELETE FROM conversations WHERE user_id = $1 AND mode = $2"
    await execute_query(query, user_id, mode)


# ──────────────────────── Subscription / Premium Queries ────────────────────────

async def get_subscription(user_id: int) -> Optional[Dict[str, Any]]:
    """Get a user's subscription record."""
    query = "SELECT * FROM subscriptions WHERE user_id = $1"
    row = await execute_fetchrow(query, user_id)
    return dict(row) if row else None


async def upsert_subscription(
    user_id: int,
    tier: str,
    expires_at: Optional[datetime],
    payment_provider: Optional[str] = None,
    payment_id: Optional[str] = None,
) -> None:
    """Create or update a subscription."""
    query = """
        INSERT INTO subscriptions
            (user_id, tier, expires_at, payment_provider, payment_id, updated_at)
        VALUES ($1, $2, $3, $4, $5, CURRENT_TIMESTAMP)
        ON CONFLICT (user_id) DO UPDATE
        SET tier = EXCLUDED.tier,
            expires_at = EXCLUDED.expires_at,
            payment_provider = EXCLUDED.payment_provider,
            payment_id = EXCLUDED.payment_id,
            updated_at = CURRENT_TIMESTAMP
    """
    await execute_query(query, user_id, tier, expires_at, payment_provider, payment_id)


async def is_premium_active(user_id: int) -> bool:
    """Check whether the user has an active premium subscription."""
    query = """
        SELECT 1 FROM subscriptions
        WHERE user_id = $1
          AND tier = 'premium'
          AND (expires_at IS NULL OR expires_at > NOW())
    """
    row = await execute_fetchval(query, user_id)
    return row is not None


# ──────────────────────── Daily-usage / Limits ────────────────────────

async def get_daily_usage(user_id: int, usage_date: Optional[date] = None) -> Dict[str, int]:
    """Get a user's usage counts for a given day (default: today)."""
    if usage_date is None:
        usage_date = date.today()
    query = """
        SELECT ai_messages, journal_entries
        FROM daily_usage
        WHERE user_id = $1 AND usage_date = $2
    """
    row = await execute_fetchrow(query, user_id, usage_date)
    if row:
        return {"ai_messages": row["ai_messages"], "journal_entries": row["journal_entries"]}
    return {"ai_messages": 0, "journal_entries": 0}


async def increment_ai_usage(user_id: int) -> int:
    """Increment today's AI message count and return the new total."""
    query = """
        INSERT INTO daily_usage (user_id, usage_date, ai_messages)
        VALUES ($1, CURRENT_DATE, 1)
        ON CONFLICT (user_id, usage_date) DO UPDATE
        SET ai_messages = daily_usage.ai_messages + 1
        RETURNING ai_messages
    """
    return await execute_fetchval(query, user_id)


async def increment_journal_usage(user_id: int) -> int:
    """Increment today's journal entry count and return the new total."""
    query = """
        INSERT INTO daily_usage (user_id, usage_date, journal_entries)
        VALUES ($1, CURRENT_DATE, 1)
        ON CONFLICT (user_id, usage_date) DO UPDATE
        SET journal_entries = daily_usage.journal_entries + 1
        RETURNING journal_entries
    """
    return await execute_fetchval(query, user_id)


# ──────────────────────── Exam Profile Queries ────────────────────────

async def get_exam_profile(user_id: int) -> Optional[Dict[str, Any]]:
    """Get a user's exam profile."""
    query = "SELECT * FROM exam_profiles WHERE user_id = $1"
    row = await execute_fetchrow(query, user_id)
    return dict(row) if row else None


async def upsert_exam_profile(
    user_id: int,
    exam_type: str,
    subjects: Optional[List[str]] = None,
    exam_date: Optional[date] = None,
    target_score: Optional[str] = None,
    current_level: str = "intermediate",
    daily_study_hours: int = 4,
) -> None:
    """Create or update a user's exam profile."""
    query = """
        INSERT INTO exam_profiles
            (user_id, exam_type, subjects, exam_date, target_score,
             current_level, daily_study_hours, updated_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, CURRENT_TIMESTAMP)
        ON CONFLICT (user_id) DO UPDATE
        SET exam_type = EXCLUDED.exam_type,
            subjects = EXCLUDED.subjects,
            exam_date = EXCLUDED.exam_date,
            target_score = EXCLUDED.target_score,
            current_level = EXCLUDED.current_level,
            daily_study_hours = EXCLUDED.daily_study_hours,
            updated_at = CURRENT_TIMESTAMP
    """
    await execute_query(
        query, user_id, exam_type, subjects or [], exam_date,
        target_score, current_level, daily_study_hours,
    )


async def delete_exam_profile(user_id: int) -> None:
    """Delete a user's exam profile."""
    await execute_query("DELETE FROM exam_profiles WHERE user_id = $1", user_id)


# ──────────────────────── Career Profile Queries ────────────────────────

async def get_career_profile(user_id: int) -> Optional[Dict[str, Any]]:
    """Get a user's career profile."""
    query = "SELECT * FROM career_profiles WHERE user_id = $1"
    row = await execute_fetchrow(query, user_id)
    return dict(row) if row else None


async def upsert_career_profile(
    user_id: int,
    status: str,
    target_role: Optional[str] = None,
    industry: Optional[str] = None,
    experience_years: int = 0,
    skills: Optional[List[str]] = None,
    languages: Optional[List[str]] = None,
    resume_text: Optional[str] = None,
) -> None:
    """Create or update a user's career profile."""
    query = """
        INSERT INTO career_profiles
            (user_id, status, target_role, industry, experience_years,
             skills, languages, resume_text, updated_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, CURRENT_TIMESTAMP)
        ON CONFLICT (user_id) DO UPDATE
        SET status = EXCLUDED.status,
            target_role = COALESCE(EXCLUDED.target_role, career_profiles.target_role),
            industry = COALESCE(EXCLUDED.industry, career_profiles.industry),
            experience_years = EXCLUDED.experience_years,
            skills = EXCLUDED.skills,
            languages = EXCLUDED.languages,
            resume_text = COALESCE(EXCLUDED.resume_text, career_profiles.resume_text),
            updated_at = CURRENT_TIMESTAMP
    """
    await execute_query(
        query, user_id, status, target_role, industry,
        experience_years, skills or [], languages or [], resume_text,
    )


async def delete_career_profile(user_id: int) -> None:
    """Delete a user's career profile."""
    await execute_query("DELETE FROM career_profiles WHERE user_id = $1", user_id)
