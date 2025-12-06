"""
Database queries for MindMate Bot
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging

from mindmate.db.connection import execute_query, execute_fetchrow, execute_fetchval

logger = logging.getLogger(__name__)


# User Queries

async def create_user(user_id: int, username: Optional[str] = None,
                     first_name: Optional[str] = None, last_name: Optional[str] = None,
                     language_code: str = "en") -> None:
    """Create a new user or update existing one."""
    query = """
        INSERT INTO users (user_id, username, first_name, last_name, language_code)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (user_id) DO UPDATE
        SET username = $2, first_name = $3, last_name = $4, last_active = CURRENT_TIMESTAMP
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


# Mood Queries

async def create_mood(user_id: int, mood_type: str, intensity: int = 5,
                     notes: Optional[str] = None) -> int:
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
    """Get mood statistics for the past N days."""
    query = """
        SELECT mood_type, COUNT(*) as count
        FROM moods
        WHERE user_id = $1 AND created_at >= NOW() - INTERVAL '%s days'
        GROUP BY mood_type
    """ % days
    rows = await execute_query(query, user_id, fetch=True)
    return {row['mood_type']: row['count'] for row in rows}


# Journal Queries

async def create_journal(user_id: int, content: str, mood: Optional[str] = None,
                        tags: Optional[List[str]] = None) -> int:
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


# Workout Queries

async def create_workout(user_id: int, activity_type: str, duration: int,
                        calories: Optional[int] = None, notes: Optional[str] = None) -> int:
    """Create a new workout entry."""
    query = """
        INSERT INTO workouts (user_id, activity_type, duration, calories, notes)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id
    """
    return await execute_fetchval(query, user_id, activity_type, duration, calories, notes)


async def get_user_workouts(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """Get user's recent workouts."""
    query = """
        SELECT * FROM workouts
        WHERE user_id = $1
        ORDER BY created_at DESC
        LIMIT $2
    """
    rows = await execute_query(query, user_id, limit, fetch=True)
    return [dict(row) for row in rows]


async def get_workout_stats(user_id: int, days: int = 7) -> Dict[str, Any]:
    """Get workout statistics."""
    query = """
        SELECT
            COUNT(*) as total_workouts,
            SUM(duration) as total_duration,
            SUM(calories) as total_calories,
            AVG(duration) as avg_duration
        FROM workouts
        WHERE user_id = $1 AND created_at >= NOW() - INTERVAL '%s days'
    """ % days
    row = await execute_fetchrow(query, user_id)
    return dict(row) if row else {}


# Expense Queries

async def create_expense(user_id: int, amount: float, category: str,
                        description: Optional[str] = None) -> int:
    """Create a new expense entry."""
    query = """
        INSERT INTO expenses (user_id, amount, category, description)
        VALUES ($1, $2, $3, $4)
        RETURNING id
    """
    return await execute_fetchval(query, user_id, amount, category, description)


async def get_user_expenses(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """Get user's recent expenses."""
    query = """
        SELECT * FROM expenses
        WHERE user_id = $1
        ORDER BY created_at DESC
        LIMIT $2
    """
    rows = await execute_query(query, user_id, limit, fetch=True)
    return [dict(row) for row in rows]


async def get_expense_stats(user_id: int, days: int = 30) -> Dict[str, Any]:
    """Get expense statistics."""
    query = """
        SELECT
            SUM(amount) as total_amount,
            AVG(amount) as avg_amount,
            COUNT(*) as total_expenses
        FROM expenses
        WHERE user_id = $1 AND created_at >= NOW() - INTERVAL '%s days'
    """ % days
    row = await execute_fetchrow(query, user_id)
    return dict(row) if row else {}


async def get_expense_by_category(user_id: int, days: int = 30) -> Dict[str, float]:
    """Get expenses grouped by category."""
    query = """
        SELECT category, SUM(amount) as total
        FROM expenses
        WHERE user_id = $1 AND created_at >= NOW() - INTERVAL '%s days'
        GROUP BY category
        ORDER BY total DESC
    """ % days
    rows = await execute_query(query, user_id, fetch=True)
    return {row['category']: float(row['total']) for row in rows}


# Reminder Queries

async def create_reminder(user_id: int, text: str, reminder_time: datetime,
                         repeat_type: str = "once") -> int:
    """Create a new reminder."""
    query = """
        INSERT INTO reminders (user_id, text, reminder_time, repeat_type)
        VALUES ($1, $2, $3, $4)
        RETURNING id
    """
    return await execute_fetchval(query, user_id, text, reminder_time, repeat_type)


async def get_pending_reminders(current_time: datetime) -> List[Dict[str, Any]]:
    """Get all pending reminders."""
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


async def get_user_reminders(user_id: int, include_sent: bool = False) -> List[Dict[str, Any]]:
    """Get user's reminders."""
    if include_sent:
        query = "SELECT * FROM reminders WHERE user_id = $1 ORDER BY reminder_time DESC LIMIT 20"
    else:
        query = "SELECT * FROM reminders WHERE user_id = $1 AND is_sent = false ORDER BY reminder_time"
    rows = await execute_query(query, user_id, fetch=True)
    return [dict(row) for row in rows]


# Conversation Queries

async def save_conversation_message(user_id: int, mode: str, role: str, content: str) -> None:
    """Save a conversation message."""
    query = """
        INSERT INTO conversations (user_id, mode, role, content)
        VALUES ($1, $2, $3, $4)
    """
    await execute_query(query, user_id, mode, role, content)


async def get_conversation_history(user_id: int, mode: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Get conversation history."""
    query = """
        SELECT * FROM conversations
        WHERE user_id = $1 AND mode = $2
        ORDER BY created_at DESC
        LIMIT $3
    """
    rows = await execute_query(query, user_id, mode, limit, fetch=True)
    return [dict(row) for row in reversed(rows)]  # Reverse to get chronological order


async def clear_conversation_history(user_id: int, mode: str) -> None:
    """Clear conversation history for a specific mode."""
    query = "DELETE FROM conversations WHERE user_id = $1 AND mode = $2"
    await execute_query(query, user_id, mode)


# Meditation Queries

async def create_meditation_session(user_id: int, duration: int,
                                   session_type: str = "mindfulness",
                                   notes: Optional[str] = None) -> int:
    """Create a new meditation session."""
    query = """
        INSERT INTO meditation_sessions (user_id, duration, session_type, notes)
        VALUES ($1, $2, $3, $4)
        RETURNING id
    """
    return await execute_fetchval(query, user_id, duration, session_type, notes)


async def get_meditation_stats(user_id: int, days: int = 30) -> Dict[str, Any]:
    """Get meditation statistics."""
    query = """
        SELECT
            COUNT(*) as total_sessions,
            SUM(duration) as total_duration,
            AVG(duration) as avg_duration
        FROM meditation_sessions
        WHERE user_id = $1 AND created_at >= NOW() - INTERVAL '%s days'
    """ % days
    row = await execute_fetchrow(query, user_id)
    return dict(row) if row else {}
