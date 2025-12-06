"""
Application constants
"""

# Bot Information
BOT_NAME = "MindMate"
BOT_VERSION = "2.0.0"
BOT_DESCRIPTION = "Your AI-powered mental health and productivity companion"

# Supported Languages
SUPPORTED_LANGUAGES = ["en", "ru", "uz"]
DEFAULT_LANGUAGE = "en"

# AI Modes
AI_MODE_FRIEND = "friend"
AI_MODE_HEALER = "healer"
AI_MODE_PRODUCTIVITY = "productivity"

AI_MODES = [AI_MODE_FRIEND, AI_MODE_HEALER, AI_MODE_PRODUCTIVITY]

# Mood Emojis
MOOD_EMOJIS = {
    "happy": "😊",
    "sad": "😢",
    "angry": "😠",
    "anxious": "😰",
    "tired": "😴",
    "excited": "🤗",
    "neutral": "😐",
    "stressed": "😫"
}

MOOD_TYPES = list(MOOD_EMOJIS.keys())

# Meditation Durations (in minutes)
MEDITATION_DURATIONS = [5, 10, 15, 20, 30]

# Fitness Activity Types
FITNESS_ACTIVITIES = [
    "running",
    "walking",
    "cycling",
    "swimming",
    "yoga",
    "gym",
    "sports",
    "other"
]

# Finance Categories
FINANCE_CATEGORIES = [
    "food",
    "transport",
    "entertainment",
    "health",
    "education",
    "shopping",
    "bills",
    "other"
]

# Statistics Periods
STATS_PERIODS = {
    "week": 7,
    "month": 30,
    "year": 365
}

# User States
USER_STATE_WAITING_MOOD = "waiting_mood"
USER_STATE_WAITING_JOURNAL = "waiting_journal"
USER_STATE_WAITING_WORKOUT = "waiting_workout"
USER_STATE_WAITING_EXPENSE = "waiting_expense"
USER_STATE_IN_HEALER_MODE = "in_healer_mode"
USER_STATE_IN_PRODUCTIVITY_MODE = "in_productivity_mode"

# Conversation Memory Limits
MAX_CONVERSATION_HISTORY = 20  # Maximum number of messages to keep in memory
CONVERSATION_TIMEOUT = 3600  # 1 hour in seconds

# Database Table Names
TABLE_USERS = "users"
TABLE_MOODS = "moods"
TABLE_JOURNALS = "journals"
TABLE_WORKOUTS = "workouts"
TABLE_EXPENSES = "expenses"
TABLE_REMINDERS = "reminders"
TABLE_CONVERSATIONS = "conversations"
TABLE_MEDITATION_SESSIONS = "meditation_sessions"

# Reminder Types
REMINDER_TYPE_ONCE = "once"
REMINDER_TYPE_DAILY = "daily"
REMINDER_TYPE_WEEKLY = "weekly"
REMINDER_TYPE_MONTHLY = "monthly"

# Time Formats
TIME_FORMAT_12H = "%I:%M %p"
TIME_FORMAT_24H = "%H:%M"
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Limits
MAX_JOURNAL_LENGTH = 5000
MAX_REMINDER_TEXT_LENGTH = 500
MAX_EXPENSE_AMOUNT = 1000000
MIN_WORKOUT_DURATION = 1  # minutes
MAX_WORKOUT_DURATION = 600  # minutes

# Pagination
ITEMS_PER_PAGE = 10

# Cache TTL (in seconds)
CACHE_TTL_SHORT = 300  # 5 minutes
CACHE_TTL_MEDIUM = 1800  # 30 minutes
CACHE_TTL_LONG = 3600  # 1 hour

# Error Messages
ERROR_GENERIC = "An error occurred. Please try again later."
ERROR_DATABASE = "Database error. Please contact support."
ERROR_AI = "AI service is temporarily unavailable."
ERROR_PERMISSION = "You don't have permission to perform this action."
ERROR_INVALID_INPUT = "Invalid input. Please try again."

# Success Messages
SUCCESS_SAVED = "Successfully saved!"
SUCCESS_DELETED = "Successfully deleted!"
SUCCESS_UPDATED = "Successfully updated!"
