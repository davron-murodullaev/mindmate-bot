import os
import logging
import psycopg2
import json
import asyncio
from datetime import datetime, time, timedelta
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from openai import OpenAI
from languages import get_text, get_mood_response, TRANSLATIONS
from fitness import get_workout_text, get_workout_buttons, get_workout_done, get_workout_stats_label
from healer import get_healer_prompt, get_healer_buttons
from ai_brain import get_master_prompt
from reminders import (
    get_reminder_text, get_reminder_menu_keyboard, get_time_keyboard,
    get_mood_keyboard_for_reminder, format_reminder_list,
    get_reminder_type_name, get_reminder_emoji
)

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === ENVIRONMENT VARIABLES ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# === CONSTANTS ===
# Language settings
DEFAULT_LANGUAGE = "uz"

# Message limits
MAX_MESSAGE_LENGTH = 4000
MAX_JOURNAL_LENGTH = 10000

# History and memory limits
CONVERSATION_HISTORY_LIMIT = 30
IMPORTANT_CONVERSATION_LIMIT = 10
MEMORY_LIMIT = 50
MOOD_HISTORY_LIMIT = 7
MOOD_HISTORY_DISPLAY_LIMIT = 5
TOP_MEMORIES_DISPLAY = 5
RECENT_CONVERSATIONS_FOR_AI = 20
RECENT_CONVERSATIONS_LIMIT = 10

# AI settings
AI_MODEL = "gpt-3.5-turbo"
AI_MAX_TOKENS = 600
AI_TEMPERATURE = 0.8
AI_EXTRACTION_MAX_TOKENS = 200
AI_EXTRACTION_TEMPERATURE = 0.3

# Importance levels
IMPORTANCE_NORMAL = 1
IMPORTANCE_MEDIUM = 2
IMPORTANCE_HIGH = 3

# Scheduler settings
REMINDER_CHECK_INTERVAL_SECONDS = 60

# UI constants
MOOD_EMOJI_INDEX_MAX = 4

client = OpenAI(api_key=OPENAI_API_KEY)

# === DATABASE ===

def get_db() -> Optional[psycopg2.extensions.connection]:
    """Ma'lumotlar bazasiga ulanish (PostgreSQL connection)."""
    try:
        return psycopg2.connect(DATABASE_URL, sslmode="require")
    except Exception as e:
        logger.error(f"DB xato: {e}")
        return None

def init_db() -> None:
    """Ma'lumotlar bazasini boshlang'ich holatga keltirish (initialize tables and indexes)."""
    conn = get_db()
    if conn is None:
        return
    cur = conn.cursor()
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            language TEXT DEFAULT 'uz',
            profile_data JSONB DEFAULT '{}',
            timezone TEXT DEFAULT 'Asia/Tashkent',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS moods (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            score INTEGER,
            note TEXT,
            context TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS journals (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            text TEXT,
            ai_analysis TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            role TEXT,
            content TEXT,
            mode TEXT DEFAULT 'normal',
            importance INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS workouts (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            workout_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS healer_sessions (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            problem_type TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS user_memories (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            memory_type TEXT,
            memory_key TEXT,
            memory_value TEXT,
            importance INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT unique_user_memory UNIQUE (user_id, memory_type, memory_key)
        )
    ''')
    
    # YANGI: Eslatmalar jadvali
    cur.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            reminder_type TEXT,
            reminder_time TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Indexlar yaratish (performance uchun)
    cur.execute('CREATE INDEX IF NOT EXISTS idx_moods_user_id ON moods(user_id)')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_journals_user_id ON journals(user_id)')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id)')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_workouts_user_id ON workouts(user_id)')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_healer_sessions_user_id ON healer_sessions(user_id)')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_user_memories_user_id ON user_memories(user_id)')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_reminders_user_id ON reminders(user_id)')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_reminders_time ON reminders(reminder_time, is_active)')

    conn.commit()
    cur.close()
    conn.close()
    logger.info("✅ Database initialized with reminders system and indexes")

# === HELPER FUNCTIONS ===

def get_user_name_from_memories(memories: List[Dict[str, Any]]) -> Optional[str]:
    """Xotiralardan foydalanuvchi ismini topish (extract user name from memories)."""
    for m in memories:
        if m["key"] == "name":
            return m["value"]
    return None

def build_mood_emoji_map() -> Dict[int, str]:
    """Kayfiyat emoji xaritasini yaratish (build mood emoji mapping)."""
    return {1: "😢", 2: "😔", 3: "😐", 4: "🙂", 5: "😄"}

def build_mood_follow_up(score: int) -> str:
    """Kayfiyatga mos follow-up xabar qaytarish (get follow-up message based on mood score)."""
    if score <= 2:
        return "\n\n💬 Nima bo'ldi? Gaplashmoqchimisiz?"
    elif score == 3:
        return "\n\n🤔 Normal kun."
    else:
        return "\n\n🌟 Ajoyib!"

# === USER FUNCTIONS ===

def save_user(user_id: int, username: str, full_name: Optional[str] = None, lang: str = DEFAULT_LANGUAGE) -> None:
    """Foydalanuvchini saqlash yoki yangilash (save or update user in database)."""
    conn = get_db()
    if conn is None:
        return
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO users (user_id, username, full_name, language, last_active)
        VALUES (%s, %s, %s, %s, NOW())
        ON CONFLICT (user_id) DO UPDATE SET
            username = %s,
            full_name = COALESCE(%s, users.full_name),
            last_active = NOW()
    ''', (user_id, username, full_name, lang, username, full_name))
    conn.commit()
    cur.close()
    conn.close()

def get_user_lang(user_id: int) -> str:
    """Foydalanuvchi tilini olish (get user's language preference)."""
    conn = get_db()
    if conn is None:
        return DEFAULT_LANGUAGE
    cur = conn.cursor()
    cur.execute('SELECT language FROM users WHERE user_id = %s', (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] if row else DEFAULT_LANGUAGE

def set_user_lang(user_id: int, lang: str) -> None:
    """Foydalanuvchi tilini o'rnatish (set user's language preference)."""
    conn = get_db()
    if conn is None:
        return
    cur = conn.cursor()
    cur.execute('UPDATE users SET language = %s WHERE user_id = %s', (lang, user_id))
    conn.commit()
    cur.close()
    conn.close()

def get_user_profile(user_id: int) -> Dict[str, Any]:
    """Foydalanuvchi profilini olish (get user profile information)."""
    conn = get_db()
    if conn is None:
        return {}
    cur = conn.cursor()
    cur.execute('SELECT username, full_name, profile_data, created_at FROM users WHERE user_id = %s', (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return {
            "username": row[0],
            "full_name": row[1],
            "profile_data": row[2] if row[2] else {},
            "member_since": row[3]
        }
    return {}

def update_user_profile(user_id: int, key: str, value: Any) -> None:
    """Foydalanuvchi profil ma'lumotlarini yangilash (update user profile data)."""
    conn = get_db()
    if conn is None:
        return
    cur = conn.cursor()
    cur.execute('''
        UPDATE users SET profile_data = profile_data || %s::jsonb WHERE user_id = %s
    ''', (json.dumps({key: value}), user_id))
    conn.commit()
    cur.close()
    conn.close()

# === MEMORY FUNCTIONS (JARVIS) ===

def save_memory(user_id: int, memory_type: str, key: str, value: str, importance: int = IMPORTANCE_NORMAL) -> None:
    """Foydalanuvchi haqida xotira saqlash (save user memory for JARVIS system)."""
    conn = get_db()
    if conn is None:
        return
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO user_memories (user_id, memory_type, memory_key, memory_value, importance)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT ON CONSTRAINT unique_user_memory DO UPDATE SET
            memory_value = %s,
            importance = %s,
            updated_at = NOW()
    ''', (user_id, memory_type, key, value, importance, value, importance))
    conn.commit()
    cur.close()
    conn.close()

def get_user_memories(user_id: int, limit: int = MEMORY_LIMIT) -> List[Dict[str, Any]]:
    """Foydalanuvchi xotiralarini olish (get user memories)."""
    conn = get_db()
    if conn is None:
        return []
    cur = conn.cursor()
    cur.execute('''
        SELECT memory_type, memory_key, memory_value, importance
        FROM user_memories WHERE user_id = %s
        ORDER BY importance DESC, updated_at DESC LIMIT %s
    ''', (user_id, limit))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"type": r[0], "key": r[1], "value": r[2], "importance": r[3]} for r in rows]

def format_memories_for_ai(memories: List[Dict[str, Any]]) -> str:
    """Xotiralarni AI uchun matn shaklida formatlash (format memories for AI prompt)."""
    if not memories:
        return "Yangi foydalanuvchi - hali ma'lumot yo'q"

    text = "📋 FOYDALANUVCHI HAQIDA BILGANLARIM:\n"
    for m in memories:
        text += f"- {m['key']}: {m['value']}\n"
    return text

# === CONVERSATION FUNCTIONS ===

def save_conversation(user_id: int, role: str, content: str, mode: str = "normal", importance: int = IMPORTANCE_NORMAL) -> None:
    """Suhbat xabarini saqlash (save conversation message to database)."""
    conn = get_db()
    if conn is None:
        return
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO conversations (user_id, role, content, mode, importance)
        VALUES (%s, %s, %s, %s, %s)
    ''', (user_id, role, content, mode, importance))
    conn.commit()
    cur.close()
    conn.close()

def get_conversations(user_id: int, limit: int = CONVERSATION_HISTORY_LIMIT) -> List[Dict[str, str]]:
    """Foydalanuvchi suhbat tarixini olish (get user conversation history)."""
    conn = get_db()
    if conn is None:
        return []
    cur = conn.cursor()
    cur.execute('''
        SELECT role, content, mode FROM conversations
        WHERE user_id = %s ORDER BY created_at DESC LIMIT %s
    ''', (user_id, limit))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"role": r[0], "content": r[1], "mode": r[2]} for r in reversed(rows)]

def get_important_conversations(user_id: int, limit: int = IMPORTANT_CONVERSATION_LIMIT) -> List[Dict[str, str]]:
    """Muhim suhbatlarni olish (get important conversations with importance >= 2)."""
    conn = get_db()
    if conn is None:
        return []
    cur = conn.cursor()
    cur.execute('''
        SELECT role, content FROM conversations
        WHERE user_id = %s AND importance >= 2
        ORDER BY created_at DESC LIMIT %s
    ''', (user_id, limit))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"role": r[0], "content": r[1]} for r in reversed(rows)]

def clear_conversations(user_id: int) -> None:
    """Suhbat tarixini tozalash (clear conversation history, keeps important ones)."""
    conn = get_db()
    if conn is None:
        return
    cur = conn.cursor()
    cur.execute('DELETE FROM conversations WHERE user_id = %s AND importance < 2', (user_id,))
    conn.commit()
    cur.close()
    conn.close()

# === MOOD & JOURNAL ===

def save_mood(user_id: int, score: int, note: Optional[str] = None, context: Optional[str] = None) -> None:
    """Kayfiyat yozuvini saqlash (save mood entry with optional note and context)."""
    conn = get_db()
    if conn is None:
        return
    cur = conn.cursor()
    cur.execute('INSERT INTO moods (user_id, score, note, context) VALUES (%s, %s, %s, %s)',
                (user_id, score, note, context))
    conn.commit()
    cur.close()
    conn.close()
    save_memory(user_id, "mood", "last_mood", f"{score}/5", importance=IMPORTANCE_NORMAL)

def save_journal(user_id: int, text: str) -> None:
    """Kundalik yozuvini saqlash (save journal entry with length validation)."""
    conn = get_db()
    if conn is None:
        return
    # Input validation: limit text length
    if len(text) > MAX_JOURNAL_LENGTH:
        text = text[:MAX_JOURNAL_LENGTH]
    cur = conn.cursor()
    cur.execute('INSERT INTO journals (user_id, text) VALUES (%s, %s)', (user_id, text))
    conn.commit()
    cur.close()
    conn.close()

def get_user_stats(user_id: int) -> Dict[str, Any]:
    """Foydalanuvchi statistikasini olish (get user statistics: mood count, average, journal count)."""
    conn = get_db()
    if conn is None:
        return {"mood_count": 0, "avg_mood": 0, "journal_count": 0}
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*), AVG(score) FROM moods WHERE user_id = %s', (user_id,))
    mood_count, avg_mood = cur.fetchone()
    cur.execute('SELECT COUNT(*) FROM journals WHERE user_id = %s', (user_id,))
    journal_count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return {
        "mood_count": mood_count or 0,
        "avg_mood": float(avg_mood) if avg_mood else 0,
        "journal_count": journal_count or 0
    }

def get_mood_history(user_id: int, limit: int = MOOD_HISTORY_LIMIT) -> List[Dict[str, Any]]:
    """Kayfiyat tarixini olish (get mood history with scores, notes, and dates)."""
    conn = get_db()
    if conn is None:
        return []
    cur = conn.cursor()
    cur.execute('''
        SELECT score, note, created_at FROM moods
        WHERE user_id = %s ORDER BY created_at DESC LIMIT %s
    ''', (user_id, limit))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"score": r[0], "note": r[1], "date": r[2]} for r in rows]

# === WORKOUT & HEALER ===

def save_workout(user_id: int, workout_type: str) -> None:
    """Mashq yozuvini saqlash (save completed workout session)."""
    conn = get_db()
    if conn is None:
        return
    cur = conn.cursor()
    cur.execute('INSERT INTO workouts (user_id, workout_type) VALUES (%s, %s)', (user_id, workout_type))
    conn.commit()
    cur.close()
    conn.close()

def get_workout_count(user_id: int) -> int:
    """Mashqlar sonini olish (get total workout count)."""
    conn = get_db()
    if conn is None:
        return 0
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM workouts WHERE user_id = %s', (user_id,))
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count or 0

def save_healer_session(user_id: int, problem_type: str, notes: Optional[str] = None) -> None:
    """Shifokor sessiyasini saqlash (save healer consultation session)."""
    conn = get_db()
    if conn is None:
        return
    cur = conn.cursor()
    cur.execute('INSERT INTO healer_sessions (user_id, problem_type, notes) VALUES (%s, %s, %s)',
                (user_id, problem_type, notes))
    conn.commit()
    cur.close()
    conn.close()
    save_memory(user_id, "health", "recent_problem", problem_type, importance=IMPORTANCE_MEDIUM)

def get_healer_count(user_id: int) -> int:
    """Shifokor sessiyalari sonini olish (get total healer session count)."""
    conn = get_db()
    if conn is None:
        return 0
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM healer_sessions WHERE user_id = %s', (user_id,))
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count or 0

# === REMINDER FUNCTIONS ===

def save_reminder(user_id: int, reminder_type: str, reminder_time: str) -> bool:
    """Eslatma saqlash (save reminder, replaces existing one of same type)."""
    conn = get_db()
    if conn is None:
        return False
    cur = conn.cursor()
    # Avvalgi eslatmani o'chirish (bir turdagi faqat bitta)
    cur.execute('DELETE FROM reminders WHERE user_id = %s AND reminder_type = %s',
                (user_id, reminder_type))
    # Yangi eslatma qo'shish
    cur.execute('''
        INSERT INTO reminders (user_id, reminder_type, reminder_time)
        VALUES (%s, %s, %s)
    ''', (user_id, reminder_type, reminder_time))
    conn.commit()
    cur.close()
    conn.close()
    return True

def get_user_reminders(user_id: int) -> List[Dict[str, str]]:
    """Foydalanuvchi eslatmalarini olish (get all active user reminders)."""
    conn = get_db()
    if conn is None:
        return []
    cur = conn.cursor()
    cur.execute('''
        SELECT reminder_type, reminder_time FROM reminders
        WHERE user_id = %s AND is_active = TRUE
        ORDER BY reminder_time
    ''', (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"type": r[0], "time": r[1]} for r in rows]

def delete_reminder(user_id: int, reminder_type: str) -> bool:
    """Eslatmani o'chirish (delete reminder by type)."""
    conn = get_db()
    if conn is None:
        return False
    cur = conn.cursor()
    cur.execute('DELETE FROM reminders WHERE user_id = %s AND reminder_type = %s',
                (user_id, reminder_type))
    conn.commit()
    cur.close()
    conn.close()
    return True

def get_reminders_for_time(current_time: str) -> List[Dict[str, Any]]:
    """Berilgan vaqt uchun eslatmalarni olish (get all reminders for specific time)."""
    conn = get_db()
    if conn is None:
        return []
    cur = conn.cursor()
    cur.execute('''
        SELECT user_id, reminder_type FROM reminders
        WHERE reminder_time = %s AND is_active = TRUE
    ''', (current_time,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"user_id": r[0], "type": r[1]} for r in rows]

def get_reminder_count(user_id: int) -> int:
    """Eslatmalar sonini olish (get total active reminder count)."""
    conn = get_db()
    if conn is None:
        return 0
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM reminders WHERE user_id = %s AND is_active = TRUE', (user_id,))
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count or 0

# === SAFE EDIT ===

async def safe_edit(query: CallbackQuery, text: str, reply_markup: Optional[InlineKeyboardMarkup] = None, parse_mode: Optional[str] = None) -> None:
    """Xabarni xavfsiz tahrirlash (safely edit message with fallbacks for errors)."""
    try:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
    except Exception as e:
        logger.error(f"Edit xato: {e}")
        try:
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=None)
        except Exception as e2:
            logger.error(f"Edit fallback 1 xato: {e2}")
            try:
                await query.message.reply_text(text, reply_markup=reply_markup, parse_mode=None)
            except Exception as e3:
                logger.error(f"Edit fallback 2 xato: {e3}")

# === NAVIGATION BUTTONS ===

def get_main_menu_button(lang: str = DEFAULT_LANGUAGE) -> InlineKeyboardMarkup:
    """Bosh menyu tugmasi (main menu button)."""
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(get_text(lang, "btn_main_menu"), callback_data="main_menu")
    ]])

def get_back_and_menu(back_to: str = "main_menu", lang: str = DEFAULT_LANGUAGE) -> InlineKeyboardMarkup:
    """Orqaga va bosh menyu tugmalari (back and main menu buttons)."""
    if back_to == "main_menu":
        return get_main_menu_button(lang)
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(get_text(lang, "btn_back"), callback_data=back_to),
        InlineKeyboardButton(get_text(lang, "btn_main_menu"), callback_data="main_menu")
    ]])

def get_main_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Asosiy menyu klaviaturasi (main menu keyboard with all options)."""
    keyboard = [
        [InlineKeyboardButton(get_text(lang, "btn_chat"), callback_data="chat"),
         InlineKeyboardButton(get_text(lang, "btn_healer"), callback_data="healer")],
        [InlineKeyboardButton(get_text(lang, "btn_mood"), callback_data="mood"),
         InlineKeyboardButton(get_text(lang, "btn_journal"), callback_data="journal")],
        [InlineKeyboardButton(get_text(lang, "btn_meditate"), callback_data="meditate"),
         InlineKeyboardButton(get_text(lang, "btn_fitness"), callback_data="fitness")],
        [InlineKeyboardButton(get_text(lang, "btn_reminders"), callback_data="reminders"),
         InlineKeyboardButton(get_text(lang, "btn_stats"), callback_data="stats")],
        [InlineKeyboardButton(get_text(lang, "btn_lang"), callback_data="lang")]
    ]
    return InlineKeyboardMarkup(keyboard)

# === AI BRAIN (JARVIS) ===

async def extract_and_save_memories(user_id: int, user_message: str, ai_response: str, lang: str) -> None:
    """Suhbatdan xotiralar ajratib olish (extract and save memories from conversation using AI)."""
    try:
        extraction_prompt = f"""
Quyidagi suhbatdan foydalanuvchi haqida muhim ma'lumotlarni ajrat.
Faqat JSON formatida javob ber, boshqa hech narsa yozma.

Foydalanuvchi xabari: {user_message}
AI javobi: {ai_response}

JSON format:
{{
    "name": "ism (agar aytilgan bo'lsa, bo'lmasa null)",
    "problem": "asosiy muammo (agar aytilgan bo'lsa)",
    "mood": "kayfiyat holati (yaxshi/yomon/neytral)",
    "interests": "qiziqishlari (agar aytilgan bo'lsa)",
    "important_fact": "muhim fakt (agar bor bo'lsa)"
}}

Agar ma'lumot bo'lmasa, null yoz. Faqat JSON, boshqa hech narsa!"""

        response = client.chat.completions.create(
            model=AI_MODEL,
            messages=[{"role": "user", "content": extraction_prompt}],
            max_tokens=AI_EXTRACTION_MAX_TOKENS,
            temperature=AI_EXTRACTION_TEMPERATURE
        )

        result = response.choices[0].message.content.strip()

        if result.startswith("{"):
            data = json.loads(result)

            if data.get("name"):
                save_memory(user_id, "personal", "name", data["name"], importance=IMPORTANCE_HIGH)
                update_user_profile(user_id, "name", data["name"])

            if data.get("problem"):
                save_memory(user_id, "health", "current_problem", data["problem"], importance=IMPORTANCE_MEDIUM)

            if data.get("mood"):
                save_memory(user_id, "mood", "current_mood", data["mood"], importance=IMPORTANCE_NORMAL)

            if data.get("interests"):
                save_memory(user_id, "personal", "interests", data["interests"], importance=IMPORTANCE_MEDIUM)

            if data.get("important_fact"):
                save_memory(user_id, "fact", "important", data["important_fact"], importance=IMPORTANCE_MEDIUM)

    except Exception as e:
        logger.error(f"Memory extraction error: {e}")

async def get_ai_response(user_id: int, message: str, mode: str = "normal") -> str:
    """AI javob olish (get AI response with full context and memory)."""
    lang = get_user_lang(user_id)

    profile = get_user_profile(user_id)
    memories = get_user_memories(user_id)
    memories_text = format_memories_for_ai(memories)

    conversations = get_conversations(user_id, limit=RECENT_CONVERSATIONS_FOR_AI)
    important_convs = get_important_conversations(user_id, limit=TOP_MEMORIES_DISPLAY)

    mood_history = get_mood_history(user_id, limit=MOOD_HISTORY_DISPLAY_LIMIT)
    mood_text = ""
    if mood_history:
        mood_text = "\n📊 KAYFIYAT TARIXI:\n"
        for m in mood_history:
            mood_text += f"- {m['date'].strftime('%d.%m')}: {m['score']}/5\n"

    if mode == "healer":
        base_prompt = get_healer_prompt(lang)
    else:
        base_prompt = get_master_prompt(lang, memories_text, "")

    user_display_name = profile.get('full_name') or profile.get('username') or "noma'lum"
    member_since = profile.get('member_since', 'yangi')

    full_context = f"""{base_prompt}

{memories_text}
{mood_text}

📝 MUHIM ESLATMALAR:
- Foydalanuvchi ismi: {user_display_name}
- Bot bilan: {member_since}dan beri

Har bir javobda:
1. Oldingi ma'lumotlardan foydalaning
2. Shaxsiylashtirilgan javob bering
3. Samimiy va foydali bo'ling"""

    messages = [{"role": "system", "content": full_context}]

    for conv in important_convs:
        messages.append(conv)

    for conv in conversations[-RECENT_CONVERSATIONS_LIMIT:]:
        messages.append({"role": conv["role"], "content": conv["content"]})

    messages.append({"role": "user", "content": message})

    try:
        response = client.chat.completions.create(
            model=AI_MODEL,
            messages=messages,
            max_tokens=AI_MAX_TOKENS,
            temperature=AI_TEMPERATURE
        )
        ai_message = response.choices[0].message.content

        importance = IMPORTANCE_MEDIUM if mode == "healer" else IMPORTANCE_NORMAL
        save_conversation(user_id, "user", message, mode, importance)
        save_conversation(user_id, "assistant", ai_message, mode, importance)

        await extract_and_save_memories(user_id, message, ai_message, lang)

        return ai_message
    except Exception as e:
        logger.error(f"OpenAI xatosi: {e}")
        return get_text(lang, "error")

# === REMINDER SCHEDULER ===

async def send_reminder_notification(app: Application, user_id: int, reminder_type: str) -> None:
    """Eslatma xabarini yuborish (send reminder notification to user)."""
    try:
        lang = get_user_lang(user_id)

        if reminder_type == "mood":
            text = get_reminder_text(lang, "mood_notify")
            keyboard = [
                [InlineKeyboardButton("😄 5", callback_data="mood_5"),
                 InlineKeyboardButton("🙂 4", callback_data="mood_4"),
                 InlineKeyboardButton("😐 3", callback_data="mood_3")],
                [InlineKeyboardButton("😔 2", callback_data="mood_2"),
                 InlineKeyboardButton("😢 1", callback_data="mood_1")],
                [InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
        elif reminder_type == "meditate":
            text = get_reminder_text(lang, "meditate_notify")
            keyboard = [
                [InlineKeyboardButton("🧘 Meditatsiya", callback_data="meditate")],
                [InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
        elif reminder_type == "workout":
            text = get_reminder_text(lang, "workout_notify")
            keyboard = [
                [InlineKeyboardButton("💪 Mashq", callback_data="fitness")],
                [InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
        elif reminder_type == "water":
            text = get_reminder_text(lang, "water_notify")
            keyboard = [[InlineKeyboardButton("✅ Ichdim", callback_data="water_done")],
                        [InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
        else:
            return

        await app.bot.send_message(chat_id=user_id, text=text, reply_markup=reply_markup)
        logger.info(f"✅ Eslatma yuborildi: {user_id} - {reminder_type}")
    except Exception as e:
        logger.error(f"Eslatma yuborishda xato: {e}")

async def check_and_send_reminders(app: Application) -> None:
    """Har daqiqada eslatmalarni tekshirish (check and send reminders every minute)."""
    while True:
        try:
            current_time = datetime.now().strftime("%H:%M")
            reminders = get_reminders_for_time(current_time)

            for reminder in reminders:
                await send_reminder_notification(app, reminder["user_id"], reminder["type"])

            # Keyingi daqiqagacha kutish
            await asyncio.sleep(REMINDER_CHECK_INTERVAL_SECONDS)
        except Exception as e:
            logger.error(f"Reminder check error: {e}")
            await asyncio.sleep(REMINDER_CHECK_INTERVAL_SECONDS)

# === COMMANDS ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start buyrug'i - Botni ishga tushirish (start bot and show main menu)."""
    user = update.effective_user
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    save_user(user.id, user.username, full_name)
    lang = get_user_lang(user.id)
    context.user_data["mode"] = "normal"

    memories = get_user_memories(user.id)
    name = get_user_name_from_memories(memories)

    if name:
        welcome = f"🌟 Xush kelibsiz, **{name}**! Sizni yana ko'rganimdan xursandman!"
    else:
        welcome = get_text(lang, "welcome")

    await update.message.reply_text(welcome, reply_markup=get_main_menu_keyboard(lang), parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/help buyrug'i - Yordam ko'rsatish (show help information)."""
    lang = get_user_lang(update.effective_user.id)
    help_text = """
🤖 **MindMate - Sizning JARVIS'ingiz**

**Imkoniyatlar:**
💬 Suhbat - Men bilan gaplashing
🌿 Shifokor - Tabiiy usullar
😊 Kayfiyat - Kayfiyatingizni kuzating
📝 Kundalik - Fikrlaringizni yozing
🧘 Meditatsiya - Tinchlanish
💪 Fitness - Mashqlar
⏰ Eslatmalar - Kunlik eslatmalar

Shunchaki yozing! ❤️
    """
    await update.message.reply_text(help_text, reply_markup=get_main_menu_button(lang), parse_mode="Markdown")

async def mood_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/mood buyrug'i - Kayfiyat tanlash (track mood)."""
    lang = get_user_lang(update.effective_user.id)
    keyboard = [
        [InlineKeyboardButton("😄 Zo'r (5)", callback_data="mood_5"),
         InlineKeyboardButton("🙂 Yaxshi (4)", callback_data="mood_4")],
        [InlineKeyboardButton("😐 Normal (3)", callback_data="mood_3"),
         InlineKeyboardButton("😔 Yomon (2)", callback_data="mood_2")],
        [InlineKeyboardButton("😢 Juda yomon (1)", callback_data="mood_1")],
        [InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]
    ]
    await update.message.reply_text(get_text(lang, "mood_ask"), reply_markup=InlineKeyboardMarkup(keyboard))

async def journal_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/journal buyrug'i - Kundalik yozish (write journal entry)."""
    lang = get_user_lang(update.effective_user.id)
    context.user_data["waiting_for"] = "journal"
    await update.message.reply_text(get_text(lang, "journal_ask"), reply_markup=get_main_menu_button(lang), parse_mode="Markdown")

async def meditate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/meditate buyrug'i - Meditatsiya tanlash (choose meditation)."""
    lang = get_user_lang(update.effective_user.id)
    keyboard = [
        [InlineKeyboardButton("🌬️ Nafas (2 daq)", callback_data="meditate_breathing"),
         InlineKeyboardButton("🧘 Tinchlanish (5 daq)", callback_data="meditate_calm")],
        [InlineKeyboardButton("😴 Uyqu (10 daq)", callback_data="meditate_sleep")],
        [InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]
    ]
    await update.message.reply_text(get_text(lang, "meditate_ask"), reply_markup=InlineKeyboardMarkup(keyboard))

async def fitness_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/fitness buyrug'i - Mashq tanlash (choose workout)."""
    lang = get_user_lang(update.effective_user.id)
    btns = get_workout_buttons(lang)
    keyboard = [
        [InlineKeyboardButton(btns["morning"], callback_data="workout_morning"),
         InlineKeyboardButton(btns["energy"], callback_data="workout_energy")],
        [InlineKeyboardButton(btns["relax"], callback_data="workout_relax")],
        [InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]
    ]
    await update.message.reply_text(btns["ask"], reply_markup=InlineKeyboardMarkup(keyboard))

async def healer_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/healer buyrug'i - Tabiiy shifokor (natural healer consultation)."""
    lang = get_user_lang(update.effective_user.id)
    context.user_data["mode"] = "healer"

    memories = get_user_memories(update.effective_user.id)
    name = get_user_name_from_memories(memories)

    if name:
        text = f"🌿 **Assalomu alaykum, {name}!**\n\nDardingizni ayting, yordam beraman. ❤️"
    else:
        text = "🌿 **Tabiiy Shifokor**\n\nDardingizni ayting, yordam beraman. ❤️"

    await update.message.reply_text(text, reply_markup=get_main_menu_button(lang), parse_mode="Markdown")

async def reminders_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/reminders buyrug'i - Eslatmalar menyusi (reminders menu)."""
    lang = get_user_lang(update.effective_user.id)
    text = get_reminder_text(lang, "reminder_menu")
    await update.message.reply_text(text, reply_markup=get_reminder_menu_keyboard(lang), parse_mode="Markdown")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/stats buyrug'i - Statistika ko'rsatish (show user statistics)."""
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    stats = get_user_stats(user_id)
    workout_count = get_workout_count(user_id)
    healer_count = get_healer_count(user_id)
    reminder_count = get_reminder_count(user_id)
    memories = get_user_memories(user_id)

    if stats["mood_count"] > 0:
        mood_emoji = ["😢", "😔", "😐", "🙂", "😄"][min(MOOD_EMOJI_INDEX_MAX, int(stats["avg_mood"]) - 1)]
    else:
        mood_emoji = "❓"

    memory_info = ""
    for m in memories[:TOP_MEMORIES_DISPLAY]:
        if m["key"] != "last_mood":
            memory_info += f"• {m['key']}: {m['value']}\n"

    stats_text = f"""
📊 **Sizning statistikangiz**

😊 Kayfiyat: {stats["mood_count"]}
📝 Kundalik: {stats["journal_count"]}
💪 Mashqlar: {workout_count}
🌿 Shifokor: {healer_count}
⏰ Eslatmalar: {reminder_count}
{f"📈 O'rtacha: {mood_emoji} ({stats['avg_mood']:.1f}/5)" if stats["mood_count"] > 0 else ""}

🧠 **Bilganlarim:**
{memory_info if memory_info else "Hali ma'lumot yo'q"}
    """
    await update.message.reply_text(stats_text, reply_markup=get_main_menu_button(lang), parse_mode="Markdown")

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/reset buyrug'i - Suhbat tarixini tozalash (clear conversation history)."""
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    clear_conversations(user_id)
    context.user_data["mode"] = "normal"
    await update.message.reply_text(get_text(lang, "reset_done") if lang != "uz" else "🔄 Suhbat tarixi tozalandi.", reply_markup=get_main_menu_button(lang))

async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/lang buyrug'i - Til tanlash (choose language)."""
    keyboard = [
        [InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz"),
         InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
         InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr"),
         InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar"),
         InlineKeyboardButton("🇮🇳 हिंदी", callback_data="lang_hi")],
        [InlineKeyboardButton("🇨🇳 中文", callback_data="lang_zh"),
         InlineKeyboardButton("🇰🇷 한국어", callback_data="lang_ko"),
         InlineKeyboardButton("🇯🇵 日本語", callback_data="lang_ja")],
        [InlineKeyboardButton("🇪🇸 Español", callback_data="lang_es"),
         InlineKeyboardButton("🇫🇷 Français", callback_data="lang_fr"),
         InlineKeyboardButton("🇩🇪 Deutsch", callback_data="lang_de")],
        [InlineKeyboardButton("🇵🇹 Português", callback_data="lang_pt")],
        [InlineKeyboardButton("🏠 Menu", callback_data="main_menu")]
    ]
    await update.message.reply_text("🌍 Tilni tanlang / Choose language:", reply_markup=InlineKeyboardMarkup(keyboard))

# === CALLBACK HANDLER ===

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lang = get_user_lang(user_id)

    # Main Menu
    if query.data == "main_menu":
        context.user_data["mode"] = "normal"
        context.user_data["waiting_for"] = None
        memories = get_user_memories(user_id)
        name = None
        for m in memories:
            if m["key"] == "name":
                name = m["value"]
                break

        if name:
            welcome = f"🏠 **Bosh Menyu**\n\n{name}, qanday yordam kerak?"
        else:
            welcome = "🏠 **Bosh Menyu**\n\nBo'limni tanlang:"

        await safe_edit(query, welcome, reply_markup=get_main_menu_keyboard(lang), parse_mode="Markdown")
        return

    # Til
    if query.data.startswith("lang_"):
        new_lang = query.data.split("_")[1]
        set_user_lang(user_id, new_lang)
        save_memory(user_id, "preferences", "language", new_lang, importance=2)
        await safe_edit(query, get_text(new_lang, "lang_changed"), reply_markup=get_main_menu_button(lang))
        return

    # Chat mode
    if query.data == "chat":
        context.user_data["mode"] = "normal"
        memories = get_user_memories(user_id)
        name = None
        for m in memories:
            if m["key"] == "name":
                name = m["value"]
                break
        
        if name:
            text = f"💬 **{name}**, men sizni tinglayman!"
        else:
            text = "💬 Men sizni tinglayman! Ismingiz nima?"
        await safe_edit(query, text, reply_markup=get_main_menu_button(lang), parse_mode="Markdown")
        return

    # Healer mode
    if query.data == "healer":
        context.user_data["mode"] = "healer"
        memories = get_user_memories(user_id)
        name = None
        recent_problem = None
        for m in memories:
            if m["key"] == "name":
                name = m["value"]
            if m["key"] == "recent_problem":
                recent_problem = m["value"]
        
        if name and recent_problem:
            text = f"🌿 **{name}**, oxirgi safar **{recent_problem}** haqida gaplashgan edik. Qanday bo'ldi?"
        elif name:
            text = f"🌿 **{name}**, tabiiy shifokoringiz sizni tinglaydi."
        else:
            text = "🌿 **Tabiiy Shifokor** sizni tinglaydi. Dardingizni ayting. ❤️"
        await safe_edit(query, text, reply_markup=get_main_menu_button(lang), parse_mode="Markdown")
        return

    # === REMINDERS ===
    if query.data == "reminders":
        text = get_reminder_text(lang, "reminder_menu")
        await safe_edit(query, text, reply_markup=get_reminder_menu_keyboard(lang), parse_mode="Markdown")
        return

    # Eslatma turini tanlash
    if query.data.startswith("remind_") and not query.data.startswith("remind_list"):
        reminder_type = query.data.replace("remind_", "")
        text = get_reminder_text(lang, "set_time")
        await safe_edit(query, text, reply_markup=get_time_keyboard(reminder_type))
        return

    # Eslatmalar ro'yxati
    if query.data == "remind_list":
        reminders = get_user_reminders(user_id)
        text = format_reminder_list(reminders, lang)
        
        # O'chirish tugmalari
        keyboard = []
        for r in reminders:
            emoji = get_reminder_emoji(r["type"])
            name = get_reminder_type_name(r["type"], lang)
            keyboard.append([InlineKeyboardButton(f"❌ {emoji} {name} - {r['time']}", 
                           callback_data=f"rdel_{r['type']}")])
        keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="reminders"),
                        InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")])
        
        await safe_edit(query, text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    # Eslatma vaqtini saqlash
    if query.data.startswith("rtime_"):
        parts = query.data.split("_")
        reminder_type = parts[1]
        reminder_time = parts[2]
        
        save_reminder(user_id, reminder_type, reminder_time)
        text = get_reminder_text(lang, "reminder_set").format(time=reminder_time)
        await safe_edit(query, text, reply_markup=get_back_and_menu("reminders", lang))
        return

    # Eslatmani o'chirish
    if query.data.startswith("rdel_"):
        reminder_type = query.data.replace("rdel_", "")
        delete_reminder(user_id, reminder_type)
        text = get_reminder_text(lang, "reminder_deleted")
        await safe_edit(query, text, reply_markup=get_back_and_menu("reminders", lang))
        return

    # Water done
    if query.data == "water_done":
        text = "💧 Zo'r! Suv ichish sog'liq uchun juda muhim! 👍"
        await safe_edit(query, text, reply_markup=get_main_menu_button(lang))
        return

    # Mood
    if query.data == "mood":
        keyboard = [
            [InlineKeyboardButton("😄 Zo'r (5)", callback_data="mood_5"),
             InlineKeyboardButton("🙂 Yaxshi (4)", callback_data="mood_4")],
            [InlineKeyboardButton("😐 Normal (3)", callback_data="mood_3"),
             InlineKeyboardButton("😔 Yomon (2)", callback_data="mood_2")],
            [InlineKeyboardButton("😢 Juda yomon (1)", callback_data="mood_1")],
            [InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]
        ]
        await safe_edit(query, get_text(lang, "mood_ask"), reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if query.data.startswith("mood_") and query.data[5:].isdigit():
        score = int(query.data.split("_")[1])
        save_mood(user_id, score)
        emojis = {1: "😢", 2: "😔", 3: "😐", 4: "🙂", 5: "😄"}

        if score <= 2:
            follow_up = "\n\n💬 Nima bo'ldi? Gaplashmoqchimisiz?"
        elif score == 3:
            follow_up = "\n\n🤔 Normal kun."
        else:
            follow_up = "\n\n🌟 Ajoyib!"

        response = f"{emojis[score]} Kayfiyat saqlandi: {score}/5{follow_up}"
        await safe_edit(query, response, reply_markup=get_back_and_menu("mood", lang))
        return

    # Journal
    if query.data == "journal":
        context.user_data["waiting_for"] = "journal"
        await safe_edit(query, get_text(lang, "journal_ask"), reply_markup=get_main_menu_button(lang), parse_mode="Markdown")
        return

    # Meditate
    if query.data == "meditate":
        keyboard = [
            [InlineKeyboardButton("🌬️ Nafas (2 daq)", callback_data="meditate_breathing"),
             InlineKeyboardButton("🧘 Tinchlanish (5 daq)", callback_data="meditate_calm")],
            [InlineKeyboardButton("😴 Uyqu (10 daq)", callback_data="meditate_sleep")],
            [InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]
        ]
        await safe_edit(query, get_text(lang, "meditate_ask"), reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if query.data == "meditate_breathing":
        text = """🌬️ **4-7-8 Nafas Mashqi**

1️⃣ Qulay o'tiring, ko'zingizni yuming
2️⃣ 4 soniya - nafas oling
3️⃣ 7 soniya - ushlab turing
4️⃣ 8 soniya - sekin chiqaring
5️⃣ 4-5 marta takrorlang

💡 Asab tizimini tinchlantiradi."""
        await safe_edit(query, text, reply_markup=get_back_and_menu("meditate", lang), parse_mode="Markdown")
        return

    if query.data == "meditate_calm":
        text = """🧘 **5 Daqiqalik Tinchlanish**

1️⃣ Qulay joyga o'tiring
2️⃣ Ko'zingizni yuming
3️⃣ Chuqur nafas oling
4️⃣ Tanangizni bo'shating
5️⃣ Faqat nafasga diqqat qiling

🕐 5 daqiqa shu holatda qoling."""
        await safe_edit(query, text, reply_markup=get_back_and_menu("meditate", lang), parse_mode="Markdown")
        return

    if query.data == "meditate_sleep":
        text = """😴 **Uyqu Meditatsiyasi**

1️⃣ 3 marta chuqur nafas oling
2️⃣ Oyoq barmoqlaridan boshlang
3️⃣ Sekin yuqoriga ko'tariling
4️⃣ Butun tana bo'sh va og'ir

🌙 Yoqimli tushlar! 💫"""
        await safe_edit(query, text, reply_markup=get_back_and_menu("meditate", lang), parse_mode="Markdown")
        return

    # Fitness
    if query.data == "fitness":
        btns = get_workout_buttons(lang)
        keyboard = [
            [InlineKeyboardButton(btns["morning"], callback_data="workout_morning"),
             InlineKeyboardButton(btns["energy"], callback_data="workout_energy")],
            [InlineKeyboardButton(btns["relax"], callback_data="workout_relax")],
            [InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]
        ]
        await safe_edit(query, btns["ask"], reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if query.data.startswith("workout_done_"):
        workout_type = query.data.split("_")[2]
        save_workout(user_id, workout_type)
        await safe_edit(query, get_workout_done(lang) + "\n\n💪 Ajoyib!", reply_markup=get_back_and_menu("fitness", lang))
        return

    if query.data.startswith("workout_"):
        workout_type = query.data.split("_")[1]
        text = get_workout_text(lang, workout_type)
        keyboard = [
            [InlineKeyboardButton("✅ Bajardim!", callback_data=f"workout_done_{workout_type}")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="fitness"),
             InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]
        ]
        await safe_edit(query, text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    # Stats
    if query.data == "stats":
        stats = get_user_stats(user_id)
        workout_count = get_workout_count(user_id)
        healer_count = get_healer_count(user_id)
        reminder_count = get_reminder_count(user_id)

        if stats["mood_count"] > 0:
            mood_emoji = ["😢", "😔", "😐", "🙂", "😄"][min(4, int(stats["avg_mood"]) - 1)]
        else:
            mood_emoji = "❓"

        stats_text = f"""
📊 **Statistika**

😊 Kayfiyat: {stats["mood_count"]}
📝 Kundalik: {stats["journal_count"]}
💪 Mashqlar: {workout_count}
🌿 Shifokor: {healer_count}
⏰ Eslatmalar: {reminder_count}
{f"📈 O'rtacha: {mood_emoji} ({stats['avg_mood']:.1f}/5)" if stats["mood_count"] > 0 else ""}
        """
        await safe_edit(query, stats_text, reply_markup=get_main_menu_button(lang), parse_mode="Markdown")
        return

    if query.data == "lang":
        keyboard = [
            [InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz"),
             InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
             InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
            [InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr"),
             InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar"),
             InlineKeyboardButton("🇮🇳 हिंदी", callback_data="lang_hi")],
            [InlineKeyboardButton("🇨🇳 中文", callback_data="lang_zh"),
             InlineKeyboardButton("🇰🇷 한국어", callback_data="lang_ko"),
             InlineKeyboardButton("🇯🇵 日本語", callback_data="lang_ja")],
            [InlineKeyboardButton("🇪🇸 Español", callback_data="lang_es"),
             InlineKeyboardButton("🇫🇷 Français", callback_data="lang_fr"),
             InlineKeyboardButton("🇩🇪 Deutsch", callback_data="lang_de")],
            [InlineKeyboardButton("🇵🇹 Português", callback_data="lang_pt")],
            [InlineKeyboardButton("🏠 Menu", callback_data="main_menu")]
        ]
        await safe_edit(query, "🌍 Tilni tanlang / Choose language:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

# === MESSAGE HANDLER ===

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Matn xabarlarini qayta ishlash (handle text messages and AI responses)."""
    user_id = update.effective_user.id
    user_message = update.message.text
    lang = get_user_lang(user_id)

    # Input validation: check message length
    if not user_message or len(user_message) > MAX_MESSAGE_LENGTH:
        await update.message.reply_text(
            get_text(lang, "error") if len(user_message) > MAX_MESSAGE_LENGTH else "⚠️ Xabar bo'sh bo'lishi mumkin emas.",
            reply_markup=get_main_menu_button(lang)
        )
        return

    if context.user_data.get("waiting_for") == "journal":
        save_journal(user_id, user_message)
        context.user_data["waiting_for"] = None
        text = get_text(lang, "journal_saved") + "\n\n💭 Yozganlaringizni eslab qolaman."
        await update.message.reply_text(text, reply_markup=get_main_menu_button(lang))
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    mode = context.user_data.get("mode", "normal")
    response = await get_ai_response(user_id, user_message, mode)
    await update.message.reply_text(response, reply_markup=get_main_menu_button(lang))

# === MAIN ===

async def post_init(app: Application) -> None:
    """Bot ishga tushgandan keyin eslatmalar schedulerini boshlash (start reminder scheduler after bot initialization)."""
    asyncio.create_task(check_and_send_reminders(app))
    logger.info("✅ Reminder scheduler started")

def main() -> None:
    """Botni ishga tushirish (start the bot application)."""
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN topilmadi!")
        return
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY topilmadi!")
        return

    if DATABASE_URL:
        init_db()

    app = Application.builder().token(TELEGRAM_TOKEN).post_init(post_init).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("mood", mood_command))
    app.add_handler(CommandHandler("journal", journal_command))
    app.add_handler(CommandHandler("meditate", meditate_command))
    app.add_handler(CommandHandler("fitness", fitness_command))
    app.add_handler(CommandHandler("healer", healer_command))
    app.add_handler(CommandHandler("reminders", reminders_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("reset", reset_command))
    app.add_handler(CommandHandler("lang", lang_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("✅ MindMate JARVIS bot ishga tushdi!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()