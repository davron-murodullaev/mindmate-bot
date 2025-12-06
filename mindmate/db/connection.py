"""
Database connection management
"""
import asyncpg
from typing import Optional
import logging

from mindmate.core.config import settings

logger = logging.getLogger(__name__)

# Global connection pool
_pool: Optional[asyncpg.Pool] = None


async def get_pool() -> asyncpg.Pool:
    """
    Get or create database connection pool.

    Returns:
        Connection pool instance
    """
    global _pool
    if _pool is None:
        _pool = await create_pool()
    return _pool


async def create_pool() -> asyncpg.Pool:
    """
    Create a new database connection pool.

    Returns:
        New connection pool instance
    """
    try:
        pool = await asyncpg.create_pool(
            settings.DATABASE_URL,
            min_size=settings.DB_POOL_MIN_SIZE,
            max_size=settings.DB_POOL_MAX_SIZE,
            command_timeout=60
        )
        logger.info("Database connection pool created successfully")
        return pool
    except Exception as e:
        logger.error(f"Failed to create database pool: {e}")
        raise


async def close_pool() -> None:
    """Close the database connection pool."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
        logger.info("Database connection pool closed")


async def init_db() -> None:
    """
    Initialize database schema.
    Creates all necessary tables if they don't exist.
    """
    pool = await get_pool()

    async with pool.acquire() as conn:
        # Create users table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username VARCHAR(255),
                first_name VARCHAR(255),
                last_name VARCHAR(255),
                language_code VARCHAR(10) DEFAULT 'en',
                timezone VARCHAR(50) DEFAULT 'UTC',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT true
            )
        """)

        # Create moods table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS moods (
                id SERIAL PRIMARY KEY,
                user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
                mood_type VARCHAR(50) NOT NULL,
                intensity INT DEFAULT 5,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create journals table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS journals (
                id SERIAL PRIMARY KEY,
                user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
                content TEXT NOT NULL,
                mood VARCHAR(50),
                tags TEXT[],
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create workouts table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS workouts (
                id SERIAL PRIMARY KEY,
                user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
                activity_type VARCHAR(100) NOT NULL,
                duration INT NOT NULL,
                calories INT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create expenses table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id SERIAL PRIMARY KEY,
                user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
                amount DECIMAL(10, 2) NOT NULL,
                category VARCHAR(100) NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create reminders table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id SERIAL PRIMARY KEY,
                user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
                text TEXT NOT NULL,
                reminder_time TIMESTAMP NOT NULL,
                repeat_type VARCHAR(50) DEFAULT 'once',
                is_sent BOOLEAN DEFAULT false,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create conversations table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id SERIAL PRIMARY KEY,
                user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
                mode VARCHAR(50) NOT NULL,
                role VARCHAR(20) NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create meditation_sessions table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS meditation_sessions (
                id SERIAL PRIMARY KEY,
                user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
                duration INT NOT NULL,
                session_type VARCHAR(100) DEFAULT 'mindfulness',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes for better performance
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_moods_user_id ON moods(user_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_moods_created_at ON moods(created_at)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_journals_user_id ON journals(user_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_workouts_user_id ON workouts(user_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_expenses_user_id ON expenses(user_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_reminders_user_id ON reminders(user_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_reminders_time ON reminders(reminder_time)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_conversations_user_mode ON conversations(user_id, mode)")

        logger.info("Database schema initialized successfully")


async def execute_query(query: str, *args, fetch: bool = False):
    """
    Execute a database query.

    Args:
        query: SQL query string
        *args: Query parameters
        fetch: Whether to fetch results

    Returns:
        Query results if fetch=True, else None
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        if fetch:
            return await conn.fetch(query, *args)
        else:
            return await conn.execute(query, *args)


async def execute_fetchrow(query: str, *args):
    """
    Execute a query and fetch a single row.

    Args:
        query: SQL query string
        *args: Query parameters

    Returns:
        Single row result
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchrow(query, *args)


async def execute_fetchval(query: str, *args):
    """
    Execute a query and fetch a single value.

    Args:
        query: SQL query string
        *args: Query parameters

    Returns:
        Single value result
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchval(query, *args)
