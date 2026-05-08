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
    """Get or create database connection pool."""
    global _pool
    if _pool is None:
        _pool = await create_pool()
    return _pool


async def create_pool() -> asyncpg.Pool:
    """Create a new database connection pool."""
    try:
        pool = await asyncpg.create_pool(
            settings.DATABASE_URL,
            min_size=settings.DB_POOL_MIN_SIZE,
            max_size=settings.DB_POOL_MAX_SIZE,
            command_timeout=60,
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
        # Users table
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

        # Moods table
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

        # Journals table
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

        # Reminders table
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

        # Conversations table
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

        # Subscriptions / Premium table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                user_id BIGINT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
                tier VARCHAR(20) DEFAULT 'free',
                expires_at TIMESTAMP,
                payment_provider VARCHAR(50),
                payment_id VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Daily usage tracking (for free-tier limits)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS daily_usage (
                user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
                usage_date DATE NOT NULL,
                ai_messages INT DEFAULT 0,
                journal_entries INT DEFAULT 0,
                PRIMARY KEY (user_id, usage_date)
            )
        """)

        # Exam profiles (DTM/IELTS/SAT/Magistratura)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS exam_profiles (
                user_id BIGINT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
                exam_type VARCHAR(20) NOT NULL,
                subjects TEXT[] DEFAULT '{}',
                exam_date DATE,
                target_score VARCHAR(20),
                current_level VARCHAR(20) DEFAULT 'intermediate',
                daily_study_hours INT DEFAULT 4,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Career profiles
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS career_profiles (
                user_id BIGINT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
                status VARCHAR(50) NOT NULL,
                target_role TEXT,
                industry TEXT,
                experience_years INT DEFAULT 0,
                skills TEXT[] DEFAULT '{}',
                languages TEXT[] DEFAULT '{}',
                resume_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Friend-finding: profiles
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS friend_profiles (
                user_id BIGINT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
                display_name VARCHAR(100) NOT NULL,
                age INT NOT NULL,
                gender VARCHAR(20),
                city VARCHAR(100),
                interests TEXT[] DEFAULT '{}',
                looking_for VARCHAR(50) NOT NULL,
                bio TEXT,
                photo_file_id VARCHAR(255),
                is_verified BOOLEAN DEFAULT false,
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Friend-finding: likes (each row = one user's reaction to another)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS friend_likes (
                from_user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
                to_user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
                is_like BOOLEAN NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (from_user_id, to_user_id)
            )
        """)

        # Friend-finding: matches (mutual likes; user1_id < user2_id always)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS friend_matches (
                user1_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
                user2_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
                matched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user1_id, user2_id),
                CHECK (user1_id < user2_id)
            )
        """)

        # Friend matching preferences (filters)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS friend_preferences (
                user_id BIGINT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
                target_gender VARCHAR(20),  -- NULL = any
                min_age INT DEFAULT 18,
                max_age INT DEFAULT 100,
                same_city_only BOOLEAN DEFAULT true,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # User blocks (user_id blocks blocked_user_id; bidirectional filtering at query time)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS friend_blocks (
                user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
                blocked_user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
                reason VARCHAR(50),  -- 'block', 'report', 'spam', etc.
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, blocked_user_id)
            )
        """)

        # Daily friend-finding usage (separate from main daily_usage so AI quota
        # and like quota are tracked independently)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS daily_friend_usage (
                user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
                usage_date DATE NOT NULL,
                likes_given INT DEFAULT 0,
                profiles_browsed INT DEFAULT 0,
                PRIMARY KEY (user_id, usage_date)
            )
        """)

        # Photo verification status — separate so we can re-verify without
        # touching the main profile.
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS photo_verifications (
                user_id BIGINT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
                is_verified BOOLEAN DEFAULT false,
                verified_at TIMESTAMP,
                last_attempt_at TIMESTAMP,
                attempts_count INT DEFAULT 0,
                ai_notes TEXT
            )
        """)

        # Indexes
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_moods_user_id ON moods(user_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_moods_created_at ON moods(created_at)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_journals_user_id ON journals(user_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_reminders_user_id ON reminders(user_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_reminders_time ON reminders(reminder_time)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_reminders_pending ON reminders(is_sent, reminder_time) WHERE is_sent = false")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_conversations_user_mode ON conversations(user_id, mode)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_conversations_created ON conversations(created_at DESC)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_friend_profiles_active ON friend_profiles(is_active, city) WHERE is_active = true")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_friend_likes_to ON friend_likes(to_user_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_friend_matches_user1 ON friend_matches(user1_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_friend_matches_user2 ON friend_matches(user2_id)")

        logger.info("Database schema initialized successfully")


async def execute_query(query: str, *args, fetch: bool = False):
    """Execute a database query."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        if fetch:
            return await conn.fetch(query, *args)
        return await conn.execute(query, *args)


async def execute_fetchrow(query: str, *args):
    """Execute a query and fetch a single row."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchrow(query, *args)


async def execute_fetchval(query: str, *args):
    """Execute a query and fetch a single value."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchval(query, *args)
