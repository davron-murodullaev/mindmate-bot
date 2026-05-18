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


async def update_user_active_status(user_id: int, is_active: bool) -> None:
    """Mark a user as active or inactive (e.g. when they block the bot)."""
    query = "UPDATE users SET is_active = $1 WHERE user_id = $2"
    await execute_query(query, is_active, user_id)


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


async def count_today_moods(user_id: int) -> int:
    """Count mood entries logged today (UTC)."""
    query = """
        SELECT COUNT(*) FROM moods
        WHERE user_id = $1
          AND created_at >= CURRENT_DATE
    """
    return await execute_fetchval(query, user_id) or 0


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
    experience_years: Optional[int] = None,
    skills: Optional[List[str]] = None,
    languages: Optional[List[str]] = None,
    resume_text: Optional[str] = None,
) -> None:
    """Create or update a user's career profile.

    Optional fields that are None are preserved on UPDATE (not overwritten).
    """
    query = """
        INSERT INTO career_profiles
            (user_id, status, target_role, industry, experience_years,
             skills, languages, resume_text, updated_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, CURRENT_TIMESTAMP)
        ON CONFLICT (user_id) DO UPDATE
        SET status = EXCLUDED.status,
            target_role = COALESCE(EXCLUDED.target_role, career_profiles.target_role),
            industry = COALESCE(EXCLUDED.industry, career_profiles.industry),
            experience_years = COALESCE(EXCLUDED.experience_years, career_profiles.experience_years),
            skills = COALESCE(EXCLUDED.skills, career_profiles.skills),
            languages = COALESCE(EXCLUDED.languages, career_profiles.languages),
            resume_text = COALESCE(EXCLUDED.resume_text, career_profiles.resume_text),
            updated_at = CURRENT_TIMESTAMP
    """
    await execute_query(
        query, user_id, status, target_role, industry,
        experience_years, skills, languages, resume_text,
    )


async def delete_career_profile(user_id: int) -> None:
    """Delete a user's career profile."""
    await execute_query("DELETE FROM career_profiles WHERE user_id = $1", user_id)


# ──────────────────────── Friend Profile Queries ────────────────────────

async def get_friend_profile(user_id: int) -> Optional[Dict[str, Any]]:
    """Get a user's friend-finding profile."""
    query = "SELECT * FROM friend_profiles WHERE user_id = $1"
    row = await execute_fetchrow(query, user_id)
    return dict(row) if row else None


async def upsert_friend_profile(
    user_id: int,
    display_name: str,
    age: int,
    looking_for: str,
    gender: Optional[str] = None,
    city: Optional[str] = None,
    interests: Optional[List[str]] = None,
    bio: Optional[str] = None,
    photo_file_ids: Optional[List[str]] = None,
    is_active: bool = True,
) -> None:
    """Create or update a friend-finding profile.

    photo_file_ids is the new multi-photo column (array of Telegram photo
    file_ids, max 3). The legacy photo_file_id column is also kept in sync
    with the first photo for backward compatibility.
    """
    photos = photo_file_ids or []
    first_photo = photos[0] if photos else None

    query = """
        INSERT INTO friend_profiles
            (user_id, display_name, age, gender, city, interests,
             looking_for, bio, photo_file_id, photo_file_ids, is_active, updated_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, CURRENT_TIMESTAMP)
        ON CONFLICT (user_id) DO UPDATE
        SET display_name = EXCLUDED.display_name,
            age = EXCLUDED.age,
            gender = EXCLUDED.gender,
            city = EXCLUDED.city,
            interests = EXCLUDED.interests,
            looking_for = EXCLUDED.looking_for,
            bio = COALESCE(EXCLUDED.bio, friend_profiles.bio),
            photo_file_id = COALESCE(EXCLUDED.photo_file_id, friend_profiles.photo_file_id),
            photo_file_ids = CASE
                WHEN array_length(EXCLUDED.photo_file_ids, 1) IS NOT NULL
                THEN EXCLUDED.photo_file_ids
                ELSE friend_profiles.photo_file_ids
            END,
            is_active = EXCLUDED.is_active,
            updated_at = CURRENT_TIMESTAMP
    """
    await execute_query(
        query, user_id, display_name, age, gender, city,
        interests or [], looking_for, bio,
        first_photo, photos, is_active,
    )


async def update_friend_photos(user_id: int, photo_file_ids: List[str]) -> None:
    """Replace the photo set on an existing profile (without touching other fields)."""
    photos = photo_file_ids or []
    first_photo = photos[0] if photos else None
    query = """
        UPDATE friend_profiles
        SET photo_file_id = $2,
            photo_file_ids = $3,
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = $1
    """
    await execute_query(query, user_id, first_photo, photos)


async def deactivate_friend_profile(user_id: int) -> None:
    """Hide profile from browsing without deleting it."""
    await execute_query(
        "UPDATE friend_profiles SET is_active = false, updated_at = CURRENT_TIMESTAMP "
        "WHERE user_id = $1",
        user_id,
    )


async def reactivate_friend_profile(user_id: int) -> None:
    """Make profile visible again."""
    await execute_query(
        "UPDATE friend_profiles SET is_active = true, updated_at = CURRENT_TIMESTAMP "
        "WHERE user_id = $1",
        user_id,
    )


async def delete_friend_profile(user_id: int) -> None:
    """Delete a user's friend profile (likes and matches cascade)."""
    await execute_query("DELETE FROM friend_profiles WHERE user_id = $1", user_id)


async def get_next_browse_profile(
    viewer_id: int,
    looking_for: Optional[str] = None,
    same_city: Optional[str] = None,
    target_gender: Optional[str] = None,
    min_age: int = 18,
    max_age: int = 100,
) -> Optional[Dict[str, Any]]:
    """
    Find the next active profile the viewer hasn't reacted to yet.

    Excludes:
      - The viewer themselves
      - Already-reacted profiles (likes/passes)
      - Blocked users (in either direction)
    Filters: looking_for, city, gender, age range.
    """
    query = """
        SELECT fp.*
        FROM friend_profiles fp
        WHERE fp.user_id != $1
          AND fp.is_active = true
          AND NOT EXISTS (
              SELECT 1 FROM friend_likes fl
              WHERE fl.from_user_id = $1 AND fl.to_user_id = fp.user_id
          )
          AND NOT EXISTS (
              SELECT 1 FROM friend_blocks fb
              WHERE (fb.user_id = $1 AND fb.blocked_user_id = fp.user_id)
                 OR (fb.user_id = fp.user_id AND fb.blocked_user_id = $1)
          )
          AND ($2::text IS NULL OR fp.looking_for = $2)
          AND ($3::text IS NULL OR LOWER(fp.city) = LOWER($3))
          AND ($4::text IS NULL OR fp.gender = $4)
          AND fp.age BETWEEN $5 AND $6
        ORDER BY RANDOM()
        LIMIT 1
    """
    row = await execute_fetchrow(
        query, viewer_id, looking_for, same_city, target_gender, min_age, max_age,
    )
    return dict(row) if row else None


async def record_friend_reaction(
    from_user_id: int,
    to_user_id: int,
    is_like: bool,
) -> bool:
    """
    Save a like/pass reaction. Returns True if a mutual match was created.
    """
    # Insert/update the reaction
    insert_query = """
        INSERT INTO friend_likes (from_user_id, to_user_id, is_like)
        VALUES ($1, $2, $3)
        ON CONFLICT (from_user_id, to_user_id) DO UPDATE
        SET is_like = EXCLUDED.is_like, created_at = CURRENT_TIMESTAMP
    """
    await execute_query(insert_query, from_user_id, to_user_id, is_like)

    if not is_like:
        return False

    # Mutual like check
    mutual_query = """
        SELECT 1 FROM friend_likes
        WHERE from_user_id = $1 AND to_user_id = $2 AND is_like = true
    """
    mutual = await execute_fetchval(mutual_query, to_user_id, from_user_id)
    if not mutual:
        return False

    # Create match (always store with user1_id < user2_id for uniqueness)
    user1, user2 = sorted([from_user_id, to_user_id])
    match_query = """
        INSERT INTO friend_matches (user1_id, user2_id)
        VALUES ($1, $2)
        ON CONFLICT (user1_id, user2_id) DO NOTHING
    """
    await execute_query(match_query, user1, user2)
    return True


async def get_friend_matches(user_id: int) -> List[Dict[str, Any]]:
    """Get the user's matches (mutual likes), with the other user's profile."""
    query = """
        SELECT fp.*, fm.matched_at
        FROM friend_matches fm
        JOIN friend_profiles fp ON fp.user_id = (
            CASE WHEN fm.user1_id = $1 THEN fm.user2_id ELSE fm.user1_id END
        )
        WHERE (fm.user1_id = $1 OR fm.user2_id = $1)
          AND fp.is_active = true
        ORDER BY fm.matched_at DESC
        LIMIT 50
    """
    rows = await execute_query(query, user_id, fetch=True)
    return [dict(row) for row in rows]


async def count_friend_likes_received(user_id: int) -> int:
    """Count how many active users have liked this user (premium feature)."""
    query = """
        SELECT COUNT(*) FROM friend_likes fl
        JOIN friend_profiles fp ON fp.user_id = fl.from_user_id
        WHERE fl.to_user_id = $1 AND fl.is_like = true AND fp.is_active = true
    """
    return await execute_fetchval(query, user_id) or 0


async def get_users_who_liked_me(user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
    """Get profiles of users who liked me (excluding mutual matches)."""
    query = """
        SELECT fp.*
        FROM friend_likes fl
        JOIN friend_profiles fp ON fp.user_id = fl.from_user_id
        WHERE fl.to_user_id = $1
          AND fl.is_like = true
          AND fp.is_active = true
          AND NOT EXISTS (
              SELECT 1 FROM friend_likes mine
              WHERE mine.from_user_id = $1 AND mine.to_user_id = fl.from_user_id
          )
        ORDER BY fl.created_at DESC
        LIMIT $2
    """
    rows = await execute_query(query, user_id, limit, fetch=True)
    return [dict(row) for row in rows]


# ──────────────────────── Friend Preferences ────────────────────────

async def get_friend_preferences(user_id: int) -> Optional[Dict[str, Any]]:
    """Get the user's matching preferences (gender, age range, geo)."""
    query = "SELECT * FROM friend_preferences WHERE user_id = $1"
    row = await execute_fetchrow(query, user_id)
    return dict(row) if row else None


async def upsert_friend_preferences(
    user_id: int,
    target_gender: Optional[str] = None,
    min_age: int = 18,
    max_age: int = 100,
    same_city_only: bool = True,
) -> None:
    """Set the user's matching preferences."""
    query = """
        INSERT INTO friend_preferences
            (user_id, target_gender, min_age, max_age, same_city_only, updated_at)
        VALUES ($1, $2, $3, $4, $5, CURRENT_TIMESTAMP)
        ON CONFLICT (user_id) DO UPDATE
        SET target_gender = EXCLUDED.target_gender,
            min_age = EXCLUDED.min_age,
            max_age = EXCLUDED.max_age,
            same_city_only = EXCLUDED.same_city_only,
            updated_at = CURRENT_TIMESTAMP
    """
    await execute_query(query, user_id, target_gender, min_age, max_age, same_city_only)


# ──────────────────────── Block / Report ────────────────────────

async def block_user(user_id: int, blocked_user_id: int, reason: str = "block") -> None:
    """Block another user; they won't appear in browse and vice-versa."""
    query = """
        INSERT INTO friend_blocks (user_id, blocked_user_id, reason)
        VALUES ($1, $2, $3)
        ON CONFLICT (user_id, blocked_user_id) DO NOTHING
    """
    await execute_query(query, user_id, blocked_user_id, reason)


async def unblock_user(user_id: int, blocked_user_id: int) -> None:
    """Unblock a previously blocked user."""
    await execute_query(
        "DELETE FROM friend_blocks WHERE user_id = $1 AND blocked_user_id = $2",
        user_id, blocked_user_id,
    )


async def is_blocked(viewer_id: int, candidate_id: int) -> bool:
    """Return True if either side has blocked the other."""
    query = """
        SELECT 1 FROM friend_blocks
        WHERE (user_id = $1 AND blocked_user_id = $2)
           OR (user_id = $2 AND blocked_user_id = $1)
        LIMIT 1
    """
    return bool(await execute_fetchval(query, viewer_id, candidate_id))


# ──────────────────────── Daily friend usage ────────────────────────

async def get_friend_daily_usage(user_id: int) -> Dict[str, int]:
    """Get today's friend-finding usage counts."""
    query = """
        SELECT likes_given, profiles_browsed
        FROM daily_friend_usage
        WHERE user_id = $1 AND usage_date = CURRENT_DATE
    """
    row = await execute_fetchrow(query, user_id)
    if row:
        return {
            "likes_given": row["likes_given"],
            "profiles_browsed": row["profiles_browsed"],
        }
    return {"likes_given": 0, "profiles_browsed": 0}


async def increment_friend_likes(user_id: int) -> int:
    """Increment today's like count and return the new total."""
    query = """
        INSERT INTO daily_friend_usage (user_id, usage_date, likes_given)
        VALUES ($1, CURRENT_DATE, 1)
        ON CONFLICT (user_id, usage_date) DO UPDATE
        SET likes_given = daily_friend_usage.likes_given + 1
        RETURNING likes_given
    """
    return await execute_fetchval(query, user_id)


# ──────────────────────── Photo verification ────────────────────────

async def get_photo_verification(user_id: int) -> Optional[Dict[str, Any]]:
    """Get a user's photo verification status."""
    query = "SELECT * FROM photo_verifications WHERE user_id = $1"
    row = await execute_fetchrow(query, user_id)
    return dict(row) if row else None


async def upsert_photo_verification(
    user_id: int,
    is_verified: bool,
    ai_notes: Optional[str] = None,
) -> None:
    """Save the result of a photo verification attempt."""
    query = """
        INSERT INTO photo_verifications
            (user_id, is_verified, verified_at, last_attempt_at, attempts_count, ai_notes)
        VALUES (
            $1, $2,
            CASE WHEN $2 THEN CURRENT_TIMESTAMP ELSE NULL END,
            CURRENT_TIMESTAMP,
            1, $3
        )
        ON CONFLICT (user_id) DO UPDATE
        SET is_verified = EXCLUDED.is_verified,
            verified_at = CASE
                WHEN EXCLUDED.is_verified THEN CURRENT_TIMESTAMP
                ELSE photo_verifications.verified_at
            END,
            last_attempt_at = CURRENT_TIMESTAMP,
            attempts_count = photo_verifications.attempts_count + 1,
            ai_notes = EXCLUDED.ai_notes
    """
    await execute_query(query, user_id, is_verified, ai_notes)
