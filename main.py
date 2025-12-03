import os
import logging
import psycopg2
import json
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from openai import OpenAI
from languages import get_text
from fitness import get_workout_text, get_workout_buttons, get_workout_done
from healer import get_healer_prompt
from ai_brain import get_master_prompt
from reminders import (
    get_reminder_text, get_reminder_menu_keyboard, get_time_keyboard,
    format_reminder_list, get_reminder_type_name, get_reminder_emoji
)

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === CONFIGURATION ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# AI Configuration
OPENAI_MODEL = "gpt-3.5-turbo"
AI_MAX_TOKENS = 600
AI_TEMPERATURE = 0.8
MEMORY_EXTRACTION_TOKENS = 200
MEMORY_EXTRACTION_TEMPERATURE = 0.3

# Data Limits
CONVERSATION_HISTORY_LIMIT = 30
IMPORTANT_CONVERSATIONS_LIMIT = 10
MEMORY_LIMIT = 50
MOOD_HISTORY_LIMIT = 7
MAX_JOURNAL_LENGTH = 10000
MAX_MESSAGE_LENGTH = 4000

# Reminder System
REMINDER_CHECK_INTERVAL = 60  # seconds

client = OpenAI(api_key=OPENAI_API_KEY)

# === DATABASE ===

def get_db():
    """
    Ma'lumotlar bazasiga ulanish yaratish.

    Returns:
        connection: PostgreSQL ulanish obyekti yoki None (xato bo'lsa)
    """
    try:
        return psycopg2.connect(DATABASE_URL, sslmode="require")
    except Exception as e:
        logger.error(f"DB xato: {e}")
        return None

def init_db():
    """
    Ma'lumotlar bazasi jadvallarini yaratish (agar mavjud bo'lmasa).

    Yaratilgan jadvallar: users, moods, journals, conversations, workouts,
    healer_sessions, user_memories, reminders va ularning indexlari.
    """
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

# === USER FUNCTIONS ===

def save_user(user_id, username, full_name=None, lang="uz"):
    """
    Foydalanuvchi ma'lumotlarini saqlash yoki yangilash.

    Args:
        user_id: Telegram foydalanuvchi ID
        username: Foydalanuvchi nomi
        full_name: To'liq ism (optional)
        lang: Til kodi (default: "uz")
    """
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

def get_user_lang(user_id):
    """
    Foydalanuvchi tilini olish.

    Args:
        user_id: Telegram foydalanuvchi ID

    Returns:
        str: Til kodi (default: "uz")
    """
    conn = get_db()
    if conn is None:
        return "uz"
    cur = conn.cursor()
    cur.execute('SELECT language FROM users WHERE user_id = %s', (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] if row else "uz"

def set_user_lang(user_id, lang):
    """
    Foydalanuvchi tilini o'zgartirish.

    Args:
        user_id: Telegram foydalanuvchi ID
        lang: Yangi til kodi
    """
    conn = get_db()
    if conn is None:
        return
    cur = conn.cursor()
    cur.execute('UPDATE users SET language = %s WHERE user_id = %s', (lang, user_id))
    conn.commit()
    cur.close()
    conn.close()

def get_user_profile(user_id):
    """
    Foydalanuvchi profilini olish.

    Args:
        user_id: Telegram foydalanuvchi ID

    Returns:
        dict: Profil ma'lumotlari (username, full_name, profile_data, member_since)
    """
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

def update_user_profile(user_id, key, value):
    """
    Foydalanuvchi profil ma'lumotlarini yangilash (JSONB formatda).

    Args:
        user_id: Telegram foydalanuvchi ID
        key: Yangilanadigan kalit
        value: Yangi qiymat
    """
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

def save_memory(user_id, memory_type, key, value, importance=1):
    """
    Foydalanuvchi haqida eslatma saqlash (JARVIS xotirasi).

    Args:
        user_id: Telegram foydalanuvchi ID
        memory_type: Xotira turi (masalan: "personal", "health", "mood")
        key: Xotira kaliti
        value: Xotira qiymati
        importance: Muhimlik darajasi (1-3, default: 1)
    """
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

def get_user_memories(user_id, limit=MEMORY_LIMIT):
    """
    Foydalanuvchi xotiralarini olish (muhimlik bo'yicha tartiblangan).

    Args:
        user_id: Telegram foydalanuvchi ID
        limit: Maksimal xotiralar soni (default: MEMORY_LIMIT)

    Returns:
        list: Xotiralar ro'yxati (dict format)
    """
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

def format_memories_for_ai(memories):
    """
    Xotiralarni AI uchun matn formatiga o'tkazish.

    Args:
        memories: Xotiralar ro'yxati

    Returns:
        str: Formatlangan matn
    """
    if not memories:
        return "Yangi foydalanuvchi - hali ma'lumot yo'q"

    text = "📋 FOYDALANUVCHI HAQIDA BILGANLARIM:\n"
    for m in memories:
        text += f"- {m['key']}: {m['value']}\n"
    return text

# === CONVERSATION FUNCTIONS ===

def save_conversation(user_id, role, content, mode="normal", importance=1):
    """
    Suhbat xabarini saqlash.

    Args:
        user_id: Telegram foydalanuvchi ID
        role: Xabar roli ("user" yoki "assistant")
        content: Xabar matni
        mode: Suhbat rejimi ("normal", "healer", va h.k.)
        importance: Muhimlik darajasi (1-3, default: 1)
    """
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

def get_conversations(user_id, limit=CONVERSATION_HISTORY_LIMIT):
    """
    Foydalanuvchi suhbat tarixini olish.

    Args:
        user_id: Telegram foydalanuvchi ID
        limit: Maksimal xabarlar soni (default: CONVERSATION_HISTORY_LIMIT)

    Returns:
        list: Suhbat xabarlari ro'yxati
    """
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

def get_important_conversations(user_id, limit=IMPORTANT_CONVERSATIONS_LIMIT):
    """
    Muhim suhbatlarni olish (importance >= 2).

    Args:
        user_id: Telegram foydalanuvchi ID
        limit: Maksimal xabarlar soni (default: IMPORTANT_CONVERSATIONS_LIMIT)

    Returns:
        list: Muhim suhbatlar ro'yxati
    """
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

def clear_conversations(user_id):
    """
    Suhbat tarixini tozalash (faqat muhim bo'lmaganlarni).

    Args:
        user_id: Telegram foydalanuvchi ID

    Note:
        Muhim suhbatlar (importance >= 2) saqlanadi
    """
    conn = get_db()
    if conn is None:
        return
    cur = conn.cursor()
    cur.execute('DELETE FROM conversations WHERE user_id = %s AND importance < 2', (user_id,))
    conn.commit()
    cur.close()
    conn.close()

# === MOOD & JOURNAL ===

def save_mood(user_id, score, note=None, context=None):
    """
    Foydalanuvchi kayfiyatini saqlash.

    Args:
        user_id: Telegram foydalanuvchi ID
        score: Kayfiyat balli (1-5)
        note: Qo'shimcha izoh (optional)
        context: Kontekst ma'lumoti (optional)
    """
    conn = get_db()
    if conn is None:
        return
    cur = conn.cursor()
    cur.execute('INSERT INTO moods (user_id, score, note, context) VALUES (%s, %s, %s, %s)',
                (user_id, score, note, context))
    conn.commit()
    cur.close()
    conn.close()
    save_memory(user_id, "mood", "last_mood", f"{score}/5", importance=1)

def save_journal(user_id, text):
    """
    Kundalik yozuvini saqlash.

    Args:
        user_id: Telegram foydalanuvchi ID
        text: Kundalik matni (max MAX_JOURNAL_LENGTH belgi)
    """
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

def get_user_stats(user_id):
    """
    Foydalanuvchi statistikasini olish.

    Args:
        user_id: Telegram foydalanuvchi ID

    Returns:
        dict: Statistika (mood_count, avg_mood, journal_count)
    """
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

def get_mood_history(user_id, limit=MOOD_HISTORY_LIMIT):
    """
    Foydalanuvchi kayfiyat tarixini olish.

    Args:
        user_id: Telegram foydalanuvchi ID
        limit: Maksimal yozuvlar soni (default: MOOD_HISTORY_LIMIT)

    Returns:
        list: Kayfiyat tarixi (score, note, date)
    """
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

def save_workout(user_id, workout_type):
    """
    Mashq seansini saqlash.

    Args:
        user_id: Telegram foydalanuvchi ID
        workout_type: Mashq turi ("morning", "energy", "relax")
    """
    conn = get_db()
    if conn is None:
        return
    cur = conn.cursor()
    cur.execute('INSERT INTO workouts (user_id, workout_type) VALUES (%s, %s)', (user_id, workout_type))
    conn.commit()
    cur.close()
    conn.close()

def get_workout_count(user_id):
    """
    Mashqlar sonini olish.

    Args:
        user_id: Telegram foydalanuvchi ID

    Returns:
        int: Mashqlar soni
    """
    conn = get_db()
    if conn is None:
        return 0
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM workouts WHERE user_id = %s', (user_id,))
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count or 0

def save_healer_session(user_id, problem_type, notes=None):
    """
    Shifokor seans ma'lumotlarini saqlash.

    Args:
        user_id: Telegram foydalanuvchi ID
        problem_type: Muammo turi
        notes: Qo'shimcha izohlar (optional)
    """
    conn = get_db()
    if conn is None:
        return
    cur = conn.cursor()
    cur.execute('INSERT INTO healer_sessions (user_id, problem_type, notes) VALUES (%s, %s, %s)',
                (user_id, problem_type, notes))
    conn.commit()
    cur.close()
    conn.close()
    save_memory(user_id, "health", "recent_problem", problem_type, importance=2)

def get_healer_count(user_id):
    """
    Shifokor seanslar sonini olish.

    Args:
        user_id: Telegram foydalanuvchi ID

    Returns:
        int: Seanslar soni
    """
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

def save_reminder(user_id, reminder_type, reminder_time):
    """Eslatma saqlash"""
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

def get_user_reminders(user_id):
    """Foydalanuvchi eslatmalarini olish"""
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

def delete_reminder(user_id, reminder_type):
    """Eslatmani o'chirish"""
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

def get_reminders_for_time(current_time):
    """Berilgan vaqt uchun eslatmalarni olish"""
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

def get_reminder_count(user_id):
    """Eslatmalar sonini olish"""
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
async def safe_edit(query, text, reply_markup=None, parse_mode=None):
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

def get_main_menu_button(lang="uz"):
    """
    Bosh menyu tugmasini yaratish.

    Args:
        lang: Til kodi (default: "uz")

    Returns:
        InlineKeyboardMarkup: Bosh menyu tugmasi
    """
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(get_text(lang, "btn_main_menu"), callback_data="main_menu")
    ]])

def get_back_and_menu(back_to="main_menu", lang="uz"):
    """
    Orqaga va Bosh menyu tugmalarini yaratish.

    Args:
        back_to: Orqaga tugmasi uchun callback_data (default: "main_menu")
        lang: Til kodi (default: "uz")

    Returns:
        InlineKeyboardMarkup: Navigatsiya tugmalari
    """
    if back_to == "main_menu":
        return get_main_menu_button(lang)
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(get_text(lang, "btn_back"), callback_data=back_to),
        InlineKeyboardButton(get_text(lang, "btn_main_menu"), callback_data="main_menu")
    ]])

def get_main_menu_keyboard(lang):
    """
    Bosh menyu klaviaturasini yaratish (barcha funksiyalar bilan).

    Args:
        lang: Til kodi

    Returns:
        InlineKeyboardMarkup: To'liq bosh menyu klaviaturasi
    """
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

async def extract_and_save_memories(user_id, user_message, ai_response, lang):
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
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": extraction_prompt}],
            max_tokens=MEMORY_EXTRACTION_TOKENS,
            temperature=MEMORY_EXTRACTION_TEMPERATURE
        )
        
        result = response.choices[0].message.content.strip()
        
        if result.startswith("{"):
            data = json.loads(result)
            
            if data.get("name"):
                save_memory(user_id, "personal", "name", data["name"], importance=3)
                update_user_profile(user_id, "name", data["name"])
            
            if data.get("problem"):
                save_memory(user_id, "health", "current_problem", data["problem"], importance=2)
            
            if data.get("mood"):
                save_memory(user_id, "mood", "current_mood", data["mood"], importance=1)
            
            if data.get("interests"):
                save_memory(user_id, "personal", "interests", data["interests"], importance=2)
            
            if data.get("important_fact"):
                save_memory(user_id, "fact", "important", data["important_fact"], importance=2)
                
    except Exception as e:
        logger.error(f"Memory extraction error: {e}")

async def get_ai_response(user_id: int, message: str, mode: str = "normal") -> str:
    lang = get_user_lang(user_id)
    
    profile = get_user_profile(user_id)
    memories = get_user_memories(user_id)
    memories_text = format_memories_for_ai(memories)
    
    conversations = get_conversations(user_id, limit=20)
    important_convs = get_important_conversations(user_id, limit=5)
    
    mood_history = get_mood_history(user_id, limit=5)
    mood_text = ""
    if mood_history:
        mood_text = "\n📊 KAYFIYAT TARIXI:\n"
        for m in mood_history:
            mood_text += f"- {m['date'].strftime('%d.%m')}: {m['score']}/5\n"
    
    if mode == "healer":
        base_prompt = get_healer_prompt(lang)
    else:
        base_prompt = get_master_prompt(lang, memories_text, "")
    
    full_context = f"""{base_prompt}

{memories_text}
{mood_text}

📝 MUHIM ESLATMALAR:
- Foydalanuvchi ismi: {profile.get('full_name') or profile.get('username') or "noma'lum"}
- Bot bilan: {profile.get('member_since', 'yangi')}dan beri

Har bir javobda:
1. Oldingi ma'lumotlardan foydalaning
2. Shaxsiylashtirilgan javob bering
3. Samimiy va foydali bo'ling"""
    
    messages = [{"role": "system", "content": full_context}]
    
    for conv in important_convs:
        messages.append(conv)
    
    for conv in conversations[-10:]:
        messages.append({"role": conv["role"], "content": conv["content"]})
    
    messages.append({"role": "user", "content": message})
    
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            max_tokens=AI_MAX_TOKENS,
            temperature=AI_TEMPERATURE
        )
        ai_message = response.choices[0].message.content
        
        importance = 2 if mode == "healer" else 1
        save_conversation(user_id, "user", message, mode, importance)
        save_conversation(user_id, "assistant", ai_message, mode, importance)
        
        await extract_and_save_memories(user_id, message, ai_message, lang)
        
        return ai_message
    except Exception as e:
        logger.error(f"OpenAI xatosi: {e}")
        return get_text(lang, "error")

# === REMINDER SCHEDULER ===

async def send_reminder_notification(app, user_id, reminder_type):
    """Eslatma xabarini yuborish"""
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

async def check_and_send_reminders(app):
    """Har daqiqada eslatmalarni tekshirish"""
    while True:
        try:
            current_time = datetime.now().strftime("%H:%M")
            reminders = get_reminders_for_time(current_time)
            
            for reminder in reminders:
                await send_reminder_notification(app, reminder["user_id"], reminder["type"])

            # Keyingi daqiqagacha kutish
            await asyncio.sleep(REMINDER_CHECK_INTERVAL)
        except Exception as e:
            logger.error(f"Reminder check error: {e}")
            await asyncio.sleep(REMINDER_CHECK_INTERVAL)

# === COMMANDS ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /start buyrug'i - botni ishga tushirish va bosh menyuni ko'rsatish.
    """
    user = update.effective_user
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    save_user(user.id, user.username, full_name)
    lang = get_user_lang(user.id)
    context.user_data["mode"] = "normal"

    memories = get_user_memories(user.id)
    name = None
    for m in memories:
        if m["key"] == "name":
            name = m["value"]
            break

    if name:
        welcome = f"🌟 Xush kelibsiz, **{name}**! Sizni yana ko'rganimdan xursandman!"
    else:
        welcome = get_text(lang, "welcome")

    await update.message.reply_text(welcome, reply_markup=get_main_menu_keyboard(lang), parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /help buyrug'i - bot imkoniyatlari haqida ma'lumot.
    """
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

async def mood_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /mood buyrug'i - kayfiyat tanlash menyusini ko'rsatish.
    """
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

async def journal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /journal buyrug'i - kundalik yozish rejimini yoqish.
    """
    lang = get_user_lang(update.effective_user.id)
    context.user_data["waiting_for"] = "journal"
    await update.message.reply_text(get_text(lang, "journal_ask"), reply_markup=get_main_menu_button(lang), parse_mode="Markdown")

async def meditate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /meditate buyrug'i - meditatsiya menyusini ko'rsatish.
    """
    lang = get_user_lang(update.effective_user.id)
    keyboard = [
        [InlineKeyboardButton("🌬️ Nafas (2 daq)", callback_data="meditate_breathing"),
         InlineKeyboardButton("🧘 Tinchlanish (5 daq)", callback_data="meditate_calm")],
        [InlineKeyboardButton("😴 Uyqu (10 daq)", callback_data="meditate_sleep")],
        [InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]
    ]
    await update.message.reply_text(get_text(lang, "meditate_ask"), reply_markup=InlineKeyboardMarkup(keyboard))

async def fitness_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /fitness buyrug'i - mashq turlari menyusini ko'rsatish.
    """
    lang = get_user_lang(update.effective_user.id)
    btns = get_workout_buttons(lang)
    keyboard = [
        [InlineKeyboardButton(btns["morning"], callback_data="workout_morning"),
         InlineKeyboardButton(btns["energy"], callback_data="workout_energy")],
        [InlineKeyboardButton(btns["relax"], callback_data="workout_relax")],
        [InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]
    ]
    await update.message.reply_text(btns["ask"], reply_markup=InlineKeyboardMarkup(keyboard))

async def healer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /healer buyrug'i - tabiiy shifokor rejimini yoqish.
    """
    lang = get_user_lang(update.effective_user.id)
    context.user_data["mode"] = "healer"

    memories = get_user_memories(update.effective_user.id)
    name = None
    for m in memories:
        if m["key"] == "name":
            name = m["value"]
            break

    if name:
        text = f"🌿 **Assalomu alaykum, {name}!**\n\nDardingizni ayting, yordam beraman. ❤️"
    else:
        text = "🌿 **Tabiiy Shifokor**\n\nDardingizni ayting, yordam beraman. ❤️"

    await update.message.reply_text(text, reply_markup=get_main_menu_button(lang), parse_mode="Markdown")

async def reminders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /reminders buyrug'i - eslatmalar menyusini ko'rsatish.
    """
    lang = get_user_lang(update.effective_user.id)
    text = get_reminder_text(lang, "reminder_menu")
    await update.message.reply_text(text, reply_markup=get_reminder_menu_keyboard(lang), parse_mode="Markdown")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /stats buyrug'i - foydalanuvchi statistikasini ko'rsatish.
    """
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    stats = get_user_stats(user_id)
    workout_count = get_workout_count(user_id)
    healer_count = get_healer_count(user_id)
    reminder_count = get_reminder_count(user_id)
    memories = get_user_memories(user_id)
    
    if stats["mood_count"] > 0:
        mood_emoji = ["😢", "😔", "😐", "🙂", "😄"][min(4, int(stats["avg_mood"]) - 1)]
    else:
        mood_emoji = "❓"
    
    memory_info = ""
    for m in memories[:5]:
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

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /reset buyrug'i - suhbat tarixini tozalash.
    """
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    clear_conversations(user_id)
    context.user_data["mode"] = "normal"
    await update.message.reply_text(get_text(lang, "reset_done") if lang != "uz" else "🔄 Suhbat tarixi tozalandi.", reply_markup=get_main_menu_button(lang))

async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /lang buyrug'i - til tanlash menyusini ko'rsatish.
    """
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

# Bosh menyu callback'ini qayta ishlash
async def handle_main_menu_callback(query, context, user_id, lang):
    """Bosh menyu tugmasini bosish"""
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

# Til tanlash callback'ini qayta ishlash
async def handle_language_callback(query, user_id, lang):
    """Til o'zgartirish yoki til menyusini ko'rsatish"""
    # Til o'zgartirish
    if query.data.startswith("lang_") and query.data != "lang":
        new_lang = query.data.split("_")[1]
        set_user_lang(user_id, new_lang)
        save_memory(user_id, "preferences", "language", new_lang, importance=2)
        await safe_edit(query, get_text(new_lang, "lang_changed"), reply_markup=get_main_menu_button(new_lang))
        return True

    # Til menyusini ko'rsatish
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
        return True

    return False

# Chat rejimini yoqish
async def handle_chat_callback(query, context, user_id, lang):
    """Oddiy chat rejimiga o'tish"""
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

# Shifokor rejimini yoqish
async def handle_healer_callback(query, context, user_id, lang):
    """Tabiiy shifokor rejimiga o'tish"""
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

# Eslatmalar bo'limi callback'larini qayta ishlash
async def handle_reminder_callback(query, user_id, lang):
    """Eslatmalar bilan bog'liq barcha callback'lar"""
    # Eslatmalar bosh menyu
    if query.data == "reminders":
        text = get_reminder_text(lang, "reminder_menu")
        await safe_edit(query, text, reply_markup=get_reminder_menu_keyboard(lang), parse_mode="Markdown")
        return True

    # Eslatma turini tanlash
    if query.data.startswith("remind_") and not query.data.startswith("remind_list"):
        reminder_type = query.data.replace("remind_", "")
        text = get_reminder_text(lang, "set_time")
        await safe_edit(query, text, reply_markup=get_time_keyboard(reminder_type))
        return True

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
        return True

    # Eslatma vaqtini saqlash
    if query.data.startswith("rtime_"):
        parts = query.data.split("_")
        reminder_type = parts[1]
        reminder_time = parts[2]

        save_reminder(user_id, reminder_type, reminder_time)
        text = get_reminder_text(lang, "reminder_set").format(time=reminder_time)
        await safe_edit(query, text, reply_markup=get_back_and_menu("reminders", lang))
        return True

    # Eslatmani o'chirish
    if query.data.startswith("rdel_"):
        reminder_type = query.data.replace("rdel_", "")
        delete_reminder(user_id, reminder_type)
        text = get_reminder_text(lang, "reminder_deleted")
        await safe_edit(query, text, reply_markup=get_back_and_menu("reminders", lang))
        return True

    # Suv ichish bajarildi
    if query.data == "water_done":
        text = "💧 Zo'r! Suv ichish sog'liq uchun juda muhim! 👍"
        await safe_edit(query, text, reply_markup=get_main_menu_button(lang))
        return True

    return False

# Kayfiyat callback'larini qayta ishlash
async def handle_mood_callback(query, user_id, lang):
    """Kayfiyat bilan bog'liq callback'lar"""
    # Kayfiyat menyu
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
        return True

    # Kayfiyat tanlash
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
        return True

    return False

# Kundalik callback'ini qayta ishlash
async def handle_journal_callback(query, context, lang):
    """Kundalik yozish rejimini yoqish"""
    if query.data == "journal":
        context.user_data["waiting_for"] = "journal"
        await safe_edit(query, get_text(lang, "journal_ask"), reply_markup=get_main_menu_button(lang), parse_mode="Markdown")
        return True
    return False

# Meditatsiya callback'larini qayta ishlash
async def handle_meditate_callback(query, lang):
    """Meditatsiya bilan bog'liq callback'lar"""
    # Meditatsiya menyu
    if query.data == "meditate":
        keyboard = [
            [InlineKeyboardButton("🌬️ Nafas (2 daq)", callback_data="meditate_breathing"),
             InlineKeyboardButton("🧘 Tinchlanish (5 daq)", callback_data="meditate_calm")],
            [InlineKeyboardButton("😴 Uyqu (10 daq)", callback_data="meditate_sleep")],
            [InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]
        ]
        await safe_edit(query, get_text(lang, "meditate_ask"), reply_markup=InlineKeyboardMarkup(keyboard))
        return True

    # Nafas mashqi
    if query.data == "meditate_breathing":
        text = """🌬️ **4-7-8 Nafas Mashqi**

1️⃣ Qulay o'tiring, ko'zingizni yuming
2️⃣ 4 soniya - nafas oling
3️⃣ 7 soniya - ushlab turing
4️⃣ 8 soniya - sekin chiqaring
5️⃣ 4-5 marta takrorlang

💡 Asab tizimini tinchlantiradi."""
        await safe_edit(query, text, reply_markup=get_back_and_menu("meditate", lang), parse_mode="Markdown")
        return True

    # Tinchlanish meditatsiyasi
    if query.data == "meditate_calm":
        text = """🧘 **5 Daqiqalik Tinchlanish**

1️⃣ Qulay joyga o'tiring
2️⃣ Ko'zingizni yuming
3️⃣ Chuqur nafas oling
4️⃣ Tanangizni bo'shating
5️⃣ Faqat nafasga diqqat qiling

🕐 5 daqiqa shu holatda qoling."""
        await safe_edit(query, text, reply_markup=get_back_and_menu("meditate", lang), parse_mode="Markdown")
        return True

    # Uyqu meditatsiyasi
    if query.data == "meditate_sleep":
        text = """😴 **Uyqu Meditatsiyasi**

1️⃣ 3 marta chuqur nafas oling
2️⃣ Oyoq barmoqlaridan boshlang
3️⃣ Sekin yuqoriga ko'tariling
4️⃣ Butun tana bo'sh va og'ir

🌙 Yoqimli tushlar! 💫"""
        await safe_edit(query, text, reply_markup=get_back_and_menu("meditate", lang), parse_mode="Markdown")
        return True

    return False

# Fitness callback'larini qayta ishlash
async def handle_fitness_callback(query, user_id, lang):
    """Fitness bilan bog'liq callback'lar"""
    # Fitness menyu
    if query.data == "fitness":
        btns = get_workout_buttons(lang)
        keyboard = [
            [InlineKeyboardButton(btns["morning"], callback_data="workout_morning"),
             InlineKeyboardButton(btns["energy"], callback_data="workout_energy")],
            [InlineKeyboardButton(btns["relax"], callback_data="workout_relax")],
            [InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]
        ]
        await safe_edit(query, btns["ask"], reply_markup=InlineKeyboardMarkup(keyboard))
        return True

    # Mashq bajarildi
    if query.data.startswith("workout_done_"):
        workout_type = query.data.split("_")[2]
        save_workout(user_id, workout_type)
        await safe_edit(query, get_workout_done(lang) + "\n\n💪 Ajoyib!", reply_markup=get_back_and_menu("fitness", lang))
        return True

    # Mashq ko'rsatish
    if query.data.startswith("workout_"):
        workout_type = query.data.split("_")[1]
        text = get_workout_text(lang, workout_type)
        keyboard = [
            [InlineKeyboardButton("✅ Bajardim!", callback_data=f"workout_done_{workout_type}")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="fitness"),
             InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]
        ]
        await safe_edit(query, text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return True

    return False

# Statistika callback'ini qayta ishlash
async def handle_stats_callback(query, user_id, lang):
    """Statistika ko'rsatish"""
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
        return True

    return False

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asosiy callback router - barcha tugma bosishlarini yo'naltiradi"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lang = get_user_lang(user_id)

    # Bosh menyu
    if query.data == "main_menu":
        await handle_main_menu_callback(query, context, user_id, lang)
        return

    # Til sozlamalari
    if query.data == "lang" or query.data.startswith("lang_"):
        if await handle_language_callback(query, user_id, lang):
            return

    # Chat rejimi
    if query.data == "chat":
        await handle_chat_callback(query, context, user_id, lang)
        return

    # Shifokor rejimi
    if query.data == "healer":
        await handle_healer_callback(query, context, user_id, lang)
        return

    # Eslatmalar bo'limi
    if (query.data == "reminders" or query.data.startswith("remind_") or
        query.data.startswith("rtime_") or query.data.startswith("rdel_") or
        query.data == "water_done"):
        if await handle_reminder_callback(query, user_id, lang):
            return

    # Kayfiyat
    if query.data == "mood" or query.data.startswith("mood_"):
        if await handle_mood_callback(query, user_id, lang):
            return

    # Kundalik
    if await handle_journal_callback(query, context, lang):
        return

    # Meditatsiya
    if query.data == "meditate" or query.data.startswith("meditate_"):
        if await handle_meditate_callback(query, lang):
            return

    # Fitness
    if query.data == "fitness" or query.data.startswith("workout_"):
        if await handle_fitness_callback(query, user_id, lang):
            return

    # Statistika
    if await handle_stats_callback(query, user_id, lang):
        return

# === MESSAGE HANDLER ===

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

async def post_init(app: Application):
    """Bot ishga tushgandan keyin eslatmalar schedulerini boshlash"""
    asyncio.create_task(check_and_send_reminders(app))
    logger.info("✅ Reminder scheduler started")

def main():
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