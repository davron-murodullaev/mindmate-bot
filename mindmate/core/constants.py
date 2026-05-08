"""
Application constants
"""

# Bot Information
BOT_NAME = "MindMate"
BOT_VERSION = "2.1.0"
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
    "stressed": "😫",
}

MOOD_TYPES = list(MOOD_EMOJIS.keys())

# Map raw emoji -> mood key (for emoji-only quick mood logging)
EMOJI_TO_MOOD = {emoji: mood for mood, emoji in MOOD_EMOJIS.items()}

# Statistics Periods
STATS_PERIODS = {
    "week": 7,
    "month": 30,
    "year": 365,
}

# User States
USER_STATE_WAITING_MOOD = "waiting_mood"
USER_STATE_WAITING_JOURNAL = "waiting_journal"
USER_STATE_IN_HEALER_MODE = "in_healer_mode"
USER_STATE_IN_PRODUCTIVITY_MODE = "in_productivity_mode"
USER_STATE_WAITING_REMINDER = "waiting_reminder"

# Conversation Memory Limits
MAX_CONVERSATION_HISTORY = 20  # Maximum number of messages to keep in memory
CONVERSATION_TIMEOUT = 3600  # 1 hour in seconds

# Database Table Names
TABLE_USERS = "users"
TABLE_MOODS = "moods"
TABLE_JOURNALS = "journals"
TABLE_REMINDERS = "reminders"
TABLE_CONVERSATIONS = "conversations"
TABLE_SUBSCRIPTIONS = "subscriptions"

# Reminder Types
REMINDER_TYPE_ONCE = "once"
REMINDER_TYPE_DAILY = "daily"
REMINDER_TYPE_WEEKLY = "weekly"
REMINDER_TYPE_MONTHLY = "monthly"

REPEAT_TYPES = [
    REMINDER_TYPE_ONCE,
    REMINDER_TYPE_DAILY,
    REMINDER_TYPE_WEEKLY,
    REMINDER_TYPE_MONTHLY,
]

# Time Formats
TIME_FORMAT_12H = "%I:%M %p"
TIME_FORMAT_24H = "%H:%M"
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Limits
MAX_JOURNAL_LENGTH = 5000
MAX_REMINDER_TEXT_LENGTH = 500

# Pagination
ITEMS_PER_PAGE = 10

# Cache TTL (in seconds)
CACHE_TTL_SHORT = 300  # 5 minutes
CACHE_TTL_MEDIUM = 1800  # 30 minutes
CACHE_TTL_LONG = 3600  # 1 hour

# ── Exam Mentor ─────────────────────────────────────────────────────
EXAM_TYPES = ["dtm", "ielts", "sat", "magistratura", "cefr"]
EXAM_TYPE_LABELS_UZ = {
    "dtm": "📚 DTM (UZ universiteti)",
    "ielts": "🌍 IELTS (ingliz tili)",
    "sat": "🇺🇸 SAT (chet el)",
    "magistratura": "🎓 Magistratura",
    "cefr": "📜 CEFR sertifikati",
}

DTM_SUBJECTS = [
    "matematika", "fizika", "kimyo", "biologiya",
    "tarix", "geografiya", "adabiyot", "ona_tili",
    "ingliz_tili", "rus_tili", "huquq", "informatika", "iqtisod",
]
DTM_SUBJECT_LABELS_UZ = {
    "matematika": "📐 Matematika",
    "fizika": "⚛️ Fizika",
    "kimyo": "🧪 Kimyo",
    "biologiya": "🧬 Biologiya",
    "tarix": "📜 Tarix",
    "geografiya": "🌍 Geografiya",
    "adabiyot": "📖 Adabiyot",
    "ona_tili": "🇺🇿 Ona tili",
    "ingliz_tili": "🇬🇧 Ingliz tili",
    "rus_tili": "🇷🇺 Rus tili",
    "huquq": "⚖️ Huquq",
    "informatika": "💻 Informatika",
    "iqtisod": "💰 Iqtisod",
}

EXAM_LEVELS = ["beginner", "intermediate", "advanced"]
EXAM_LEVEL_LABELS_UZ = {
    "beginner": "🌱 Boshlovchi",
    "intermediate": "🌿 O'rta",
    "advanced": "🌳 Yuqori",
}

# ── Career Coach ────────────────────────────────────────────────────
CAREER_STATUS_OPTIONS = ["student", "graduate", "employed", "switching", "freelance"]
CAREER_STATUS_LABELS_UZ = {
    "student": "🎓 Talaba",
    "graduate": "🎯 Bitiruvchi (ish izlamoqdaman)",
    "employed": "💼 Hozir ishlayapman",
    "switching": "🔄 Ish o'zgartirmoqchiman",
    "freelance": "🚀 Freelancer / Biznes",
}

# ── Friend Finding ──────────────────────────────────────────────────
FRIEND_LOOKING_OPTIONS = ["friendship", "relationship", "partner"]
FRIEND_LOOKING_LABELS_UZ = {
    "friendship": "🤝 Do'stlik",
    "relationship": "💕 Munosabat",
    "partner": "🚀 Hamkorlik (biznes/loyiha)",
}

FRIEND_GENDER_OPTIONS = ["male", "female", "other"]
FRIEND_GENDER_LABELS_UZ = {
    "male": "👨 Erkak",
    "female": "👩 Ayol",
    "other": "🌈 Boshqa",
}

FRIEND_INTERESTS = [
    "music", "movies", "books", "sport", "gaming",
    "tech", "art", "travel", "cooking", "photography",
    "fashion", "fitness", "languages", "business", "science",
]
FRIEND_INTERESTS_LABELS_UZ = {
    "music": "🎵 Musiqa",
    "movies": "🎬 Kino",
    "books": "📚 Kitoblar",
    "sport": "⚽ Sport",
    "gaming": "🎮 O'yinlar",
    "tech": "💻 Texnologiya",
    "art": "🎨 San'at",
    "travel": "✈️ Sayohat",
    "cooking": "🍳 Oshxona",
    "photography": "📸 Fotografiya",
    "fashion": "👗 Moda",
    "fitness": "💪 Fitnes",
    "languages": "🌍 Tillar",
    "business": "💼 Biznes",
    "science": "🔬 Ilm-fan",
}

FRIEND_MIN_AGE = 18
FRIEND_MAX_AGE = 100
FRIEND_MIN_INTERESTS = 1
FRIEND_MAX_INTERESTS = 6
FRIEND_BIO_MAX_LENGTH = 300

# Free-tier limits for friend finding
FREE_DAILY_BROWSES = 10
FREE_DAILY_LIKES = 5

# ── Subscription / Premium ──────────────────────────────────────────
SUB_TIER_FREE = "free"
SUB_TIER_PREMIUM = "premium"
SUB_TIERS = [SUB_TIER_FREE, SUB_TIER_PREMIUM]

# Free-tier daily limits
FREE_DAILY_AI_MESSAGES = 10
FREE_MAX_REMINDERS = 5
FREE_MAX_JOURNAL_ENTRIES_PER_DAY = 3

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
