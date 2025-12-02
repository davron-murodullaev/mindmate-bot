import os
import logging
import psycopg2
import json
import asyncio
from datetime import datetime, time, timedelta
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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
from content_generator import (
    create_pdf_document, create_resume_pdf, create_presentation,
    get_content_templates, get_content_text
)
from ai_tools import (
    generate_image, translate_text, generate_code, find_recipe,
    create_travel_plan, create_study_material, generate_business_idea,
    write_email, get_ai_tools_text
)
from premium import (
    init_premium_tables, get_user_subscription, check_usage_limit,
    increment_usage, get_usage_stats, get_premium_texts,
    create_referral, get_referral_stats, get_referral_code, parse_referral_code,
    SUBSCRIPTION_TIERS
)
from financial_coach import (
    init_financial_tables, add_expense, add_income, get_monthly_summary,
    get_financial_advice, analyze_spending_habits, create_budget_plan,
    get_investment_advice, check_budget_alerts, get_financial_texts
)
from productivity_ai import (
    init_productivity_tables, add_task, complete_task, get_user_tasks,
    create_daily_plan, analyze_productivity, start_focus_session,
    complete_focus_session, get_productivity_texts
)
from enhanced_features import (
    get_ai_friend_menu, get_health_menu, get_creative_tools_menu,
    get_my_profile_menu, get_settings_menu, get_quick_expense_shortcuts,
    get_expense_shortcuts_keyboard, get_referral_share_keyboard,
    get_referral_text, get_investment_disclaimer, get_ai_friend_prompt,
    get_menu_texts, add_recurring_expense
)

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

client = OpenAI(api_key=OPENAI_API_KEY)

# === DATABASE ===

def get_db():
    try:
        return psycopg2.connect(DATABASE_URL, sslmode="require")
    except Exception as e:
        logger.error(f"DB xato: {e}")
        return None

def init_db():
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

    # Initialize premium, financial, productivity tables
    conn = get_db()
    if conn:
        init_premium_tables(conn)
        init_financial_tables(conn)
        init_productivity_tables(conn)
        conn.close()

    logger.info("✅ Database initialized with all features")

# === USER FUNCTIONS ===

def save_user(user_id, username, full_name=None, lang="en"):
    """Save user with default English language"""
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
    """Get user language (default: English)"""
    conn = get_db()
    if conn is None:
        return "en"
    cur = conn.cursor()
    cur.execute('SELECT language FROM users WHERE user_id = %s', (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] if row else "en"

def set_user_lang(user_id, lang):
    conn = get_db()
    if conn is None:
        return
    cur = conn.cursor()
    cur.execute('UPDATE users SET language = %s WHERE user_id = %s', (lang, user_id))
    conn.commit()
    cur.close()
    conn.close()

def get_user_profile(user_id):
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

def get_user_memories(user_id, limit=50):
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
    if not memories:
        return "Yangi foydalanuvchi - hali ma'lumot yo'q"
    
    text = "📋 FOYDALANUVCHI HAQIDA BILGANLARIM:\n"
    for m in memories:
        text += f"- {m['key']}: {m['value']}\n"
    return text

# === CONVERSATION FUNCTIONS ===

def save_conversation(user_id, role, content, mode="normal", importance=1):
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

def get_conversations(user_id, limit=30):
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

def get_important_conversations(user_id, limit=10):
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
    conn = get_db()
    if conn is None:
        return
    # Input validation: limit text length
    if len(text) > 10000:
        text = text[:10000]
    cur = conn.cursor()
    cur.execute('INSERT INTO journals (user_id, text) VALUES (%s, %s)', (user_id, text))
    conn.commit()
    cur.close()
    conn.close()

def get_user_stats(user_id):
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

def get_mood_history(user_id, limit=7):
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
    conn = get_db()
    if conn is None:
        return
    cur = conn.cursor()
    cur.execute('INSERT INTO workouts (user_id, workout_type) VALUES (%s, %s)', (user_id, workout_type))
    conn.commit()
    cur.close()
    conn.close()

def get_workout_count(user_id):
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
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(get_text(lang, "btn_main_menu"), callback_data="main_menu")
    ]])

def get_back_and_menu(back_to="main_menu", lang="uz"):
    if back_to == "main_menu":
        return get_main_menu_button(lang)
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(get_text(lang, "btn_back"), callback_data=back_to),
        InlineKeyboardButton(get_text(lang, "btn_main_menu"), callback_data="main_menu")
    ]])

def get_main_menu_keyboard(lang):
    """Simplified main menu - 4x2 grid (language-aware)"""
    texts = {
        "en": {
            "ai_friend": "💬 AI Friend",
            "financial": "💰 Finance",
            "productivity": "⚡ Productivity",
            "creative": "🎨 Creative",
            "health": "🧘 Health",
            "profile": "📊 Profile",
            "premium": "💎 Premium",
            "settings": "⚙️ Settings"
        },
        "uz": {
            "ai_friend": "💬 AI Do'st",
            "financial": "💰 Moliya",
            "productivity": "⚡ Unumdorlik",
            "creative": "🎨 Ijod",
            "health": "🧘 Salomatlik",
            "profile": "📊 Men",
            "premium": "💎 Premium",
            "settings": "⚙️ Sozlamalar"
        }
    }

    t = texts.get(lang, texts["en"])

    keyboard = [
        [InlineKeyboardButton(t["ai_friend"], callback_data="ai_friend"),
         InlineKeyboardButton(t["financial"], callback_data="financial_menu")],
        [InlineKeyboardButton(t["productivity"], callback_data="productivity_menu"),
         InlineKeyboardButton(t["creative"], callback_data="creative_tools")],
        [InlineKeyboardButton(t["health"], callback_data="health_menu"),
         InlineKeyboardButton(t["profile"], callback_data="my_profile")],
        [InlineKeyboardButton(t["premium"], callback_data="premium_menu"),
         InlineKeyboardButton(t["settings"], callback_data="settings_menu")]
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
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": extraction_prompt}],
            max_tokens=200,
            temperature=0.3
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
    
    unknown_text = "noma'lum"
    full_name_display = profile.get('full_name') or profile.get('username') or unknown_text

    full_context = f"""{base_prompt}

{memories_text}
{mood_text}

📝 MUHIM ESLATMALAR:
- Foydalanuvchi ismi: {full_name_display}
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
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=600,
            temperature=0.8
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
            await asyncio.sleep(60)
        except Exception as e:
            logger.error(f"Reminder check error: {e}")
            await asyncio.sleep(60)

# === COMMANDS ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    lang = get_user_lang(update.effective_user.id)
    context.user_data["waiting_for"] = "journal"
    await update.message.reply_text(get_text(lang, "journal_ask"), reply_markup=get_main_menu_button(lang), parse_mode="Markdown")

async def meditate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_lang(update.effective_user.id)
    keyboard = [
        [InlineKeyboardButton("🌬️ Nafas (2 daq)", callback_data="meditate_breathing"),
         InlineKeyboardButton("🧘 Tinchlanish (5 daq)", callback_data="meditate_calm")],
        [InlineKeyboardButton("😴 Uyqu (10 daq)", callback_data="meditate_sleep")],
        [InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]
    ]
    await update.message.reply_text(get_text(lang, "meditate_ask"), reply_markup=InlineKeyboardMarkup(keyboard))

async def fitness_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    lang = get_user_lang(update.effective_user.id)
    context.user_data["mode"] = "healer"
    
    memories = get_user_memories(update.effective_user.id)
    name = None
    for m in memories:
        if m["key"] == "name":
            name = m["value"]
            break
    
    if name:
        greeting = get_text(lang, "healer_greeting_name").format(name=name)
        text = greeting
    else:
        text = get_text(lang, "healer_text")
    
    await update.message.reply_text(text, reply_markup=get_main_menu_button(lang), parse_mode="Markdown")

async def reminders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Eslatmalar buyrug'i"""
    lang = get_user_lang(update.effective_user.id)
    text = get_reminder_text(lang, "reminder_menu")
    await update.message.reply_text(text, reply_markup=get_reminder_menu_keyboard(lang), parse_mode="Markdown")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    clear_conversations(user_id)
    context.user_data["mode"] = "normal"
    await update.message.reply_text(get_text(lang, "reset_done") if lang != "uz" else "🔄 Suhbat tarixi tozalandi.", reply_markup=get_main_menu_button(lang))

async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    # === NEW ENHANCED MENUS ===

    # AI Friend (Chat + Journal + Deep Talk)
    if query.data == "ai_friend":
        texts = get_menu_texts(lang)
        await safe_edit(query, texts.get("ai_friend", "💬 AI Do'st"), reply_markup=get_ai_friend_menu(lang), parse_mode="Markdown")
        return

    if query.data == "chat_mode":
        context.user_data["mode"] = "normal"
        memories = get_user_memories(user_id)
        name = None
        for m in memories:
            if m["key"] == "name":
                name = m["value"]
                break

        if name:
            text = get_text(lang, "chat_mode_name").format(name=name)
        else:
            text = get_text(lang, "chat_mode_noname")
        await safe_edit(query, text, reply_markup=get_main_menu_button(lang), parse_mode="Markdown")
        return

    if query.data == "journal_mode":
        context.user_data["waiting_for"] = "journal"
        context.user_data["mode"] = "journal_deep"  # Deep analysis mode
        text = get_text(lang, "journal_mode")
        await safe_edit(query, text, reply_markup=get_main_menu_button(lang), parse_mode="Markdown")
        return

    if query.data == "deep_chat":
        context.user_data["mode"] = "deep_talk"
        text = get_text(lang, "deep_chat")
        await safe_edit(query, text, reply_markup=get_main_menu_button(lang), parse_mode="Markdown")
        return

    # Health Menu
    if query.data == "health_menu":
        texts = get_menu_texts(lang)
        await safe_edit(query, texts.get("health", "🧘 Salomatlik"), reply_markup=get_health_menu(lang), parse_mode="Markdown")
        return

    # Creative Tools
    if query.data == "creative_tools":
        texts = get_menu_texts(lang)
        await safe_edit(query, texts.get("creative", "🎨 Ijod"), reply_markup=get_creative_tools_menu(lang), parse_mode="Markdown")
        return

    # My Profile
    if query.data == "my_profile":
        stats = get_user_stats(user_id)
        await safe_edit(query, "📊 **Mening Profilim**", reply_markup=get_my_profile_menu(stats, lang), parse_mode="Markdown")
        return

    # Settings
    if query.data == "settings_menu":
        await safe_edit(query, "⚙️ **Sozlamalar**", reply_markup=get_settings_menu(lang), parse_mode="Markdown")
        return

    # Chat mode (old - compatibility)
    if query.data == "chat":
        # Redirect to AI Friend
        texts = get_menu_texts(lang)
        await safe_edit(query, texts.get("ai_friend", "💬 AI Do'st"), reply_markup=get_ai_friend_menu(lang), parse_mode="Markdown")
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
            text = get_text(lang, "healer_remember_problem").format(name=name, problem=recent_problem)
        elif name:
            text = get_text(lang, "healer_listening_name").format(name=name)
        else:
            text = get_text(lang, "healer_text")
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
        text = get_text(lang, "breathing")
        await safe_edit(query, text, reply_markup=get_back_and_menu("meditate", lang), parse_mode="Markdown")
        return

    if query.data == "meditate_calm":
        text = get_text(lang, "calm")
        await safe_edit(query, text, reply_markup=get_back_and_menu("meditate", lang), parse_mode="Markdown")
        return

    if query.data == "meditate_sleep":
        text = get_text(lang, "sleep")
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

    # === CONTENT MENU (PDF/PPT) ===
    if query.data == "content_menu":
        keyboard = [
            [InlineKeyboardButton(f"📄 {get_text(lang, 'btn_create_pdf')}", callback_data="create_pdf"),
             InlineKeyboardButton(f"📊 {get_text(lang, 'btn_create_ppt')}", callback_data="create_ppt")],
            [InlineKeyboardButton(f"📋 {get_text(lang, 'btn_create_resume')}", callback_data="create_resume")],
            [InlineKeyboardButton(f"🏠 {get_text(lang, 'btn_main_menu')}", callback_data="main_menu")]
        ]
        text = get_text(lang, "create_document")
        await safe_edit(query, text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    if query.data == "create_pdf":
        context.user_data["waiting_for"] = "pdf_title"
        text = get_text(lang, "create_pdf_title")
        await safe_edit(query, text, reply_markup=get_main_menu_button(lang), parse_mode="Markdown")
        return

    if query.data == "create_ppt":
        context.user_data["waiting_for"] = "ppt_title"
        text = get_text(lang, "create_presentation_title")
        await safe_edit(query, text, reply_markup=get_main_menu_button(lang), parse_mode="Markdown")
        return

    if query.data == "create_resume":
        context.user_data["waiting_for"] = "resume_name"
        text = get_text(lang, "create_resume_name")
        await safe_edit(query, text, reply_markup=get_main_menu_button(lang), parse_mode="Markdown")
        return

    # === AI TOOLS MENU ===
    if query.data == "ai_tools_menu":
        keyboard = [
            [InlineKeyboardButton(f"🎨 {get_text(lang, 'btn_create_image')}", callback_data="ai_image"),
             InlineKeyboardButton(f"🌐 {get_text(lang, 'btn_translate')}", callback_data="ai_translate")],
            [InlineKeyboardButton(f"👨‍💻 {get_text(lang, 'btn_code')}", callback_data="ai_code"),
             InlineKeyboardButton(f"🍳 {get_text(lang, 'btn_recipe')}", callback_data="ai_recipe")],
            [InlineKeyboardButton(f"✈️ {get_text(lang, 'btn_travel')}", callback_data="ai_travel"),
             InlineKeyboardButton(f"📚 {get_text(lang, 'btn_study')}", callback_data="ai_study")],
            [InlineKeyboardButton(f"💼 {get_text(lang, 'btn_business')}", callback_data="ai_business"),
             InlineKeyboardButton(f"✉️ {get_text(lang, 'btn_email')}", callback_data="ai_email")],
            [InlineKeyboardButton(f"🏠 {get_text(lang, 'btn_main_menu')}", callback_data="main_menu")]
        ]
        text = get_text(lang, "ai_tools_menu")
        await safe_edit(query, text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    if query.data == "ai_image":
        context.user_data["waiting_for"] = "image_prompt"
        text = get_text(lang, "create_image_prompt")
        await safe_edit(query, text, reply_markup=get_main_menu_button(lang), parse_mode="Markdown")
        return

    if query.data == "ai_translate":
        context.user_data["waiting_for"] = "translate_text"
        text = get_text(lang, "translate_prompt")
        await safe_edit(query, text, reply_markup=get_main_menu_button(lang), parse_mode="Markdown")
        return

    if query.data == "ai_code":
        context.user_data["waiting_for"] = "code_description"
        text = get_text(lang, "write_code_prompt")
        await safe_edit(query, text, reply_markup=get_main_menu_button(lang), parse_mode="Markdown")
        return

    if query.data == "ai_recipe":
        context.user_data["waiting_for"] = "recipe_name"
        text = get_text(lang, "find_recipe_prompt")
        await safe_edit(query, text, reply_markup=get_main_menu_button(lang), parse_mode="Markdown")
        return

    if query.data == "ai_travel":
        context.user_data["waiting_for"] = "travel_destination"
        text = get_text(lang, "travel_plan_prompt")
        await safe_edit(query, text, reply_markup=get_main_menu_button(lang), parse_mode="Markdown")
        return

    if query.data == "ai_study":
        context.user_data["waiting_for"] = "study_topic"
        text = get_text(lang, "study_material_prompt")
        await safe_edit(query, text, reply_markup=get_main_menu_button(lang), parse_mode="Markdown")
        return

    if query.data == "ai_business":
        context.user_data["waiting_for"] = "business_industry"
        text = get_text(lang, "business_idea_prompt")
        await safe_edit(query, text, reply_markup=get_main_menu_button(lang), parse_mode="Markdown")
        return

    if query.data == "ai_email":
        context.user_data["waiting_for"] = "email_purpose"
        text = get_text(lang, "write_email_prompt")
        await safe_edit(query, text, reply_markup=get_main_menu_button(lang), parse_mode="Markdown")
        return

    # === PREMIUM MENU ===
    if query.data == "premium_menu":
        conn = get_db()
        if conn:
            stats = get_usage_stats(conn, user_id)
            texts = get_premium_texts(lang)

            # Format expiry date
            expires_text = ""
            if stats.get("expires_at"):
                expires_text = f"⏰ Tugaydi: {stats['expires_at'].strftime('%Y-%m-%d')}"

            # Format limits (-1 = unlimited)
            ai_limit_text = "♾️" if stats["ai_limit_daily"] == -1 else str(stats["ai_limit_daily"])
            pdf_limit_text = "♾️" if stats["pdf_limit_month"] == -1 else str(stats["pdf_limit_month"])
            img_limit_text = "♾️" if stats["images_limit_month"] == -1 else str(stats["images_limit_month"])

            usage_text = texts.get("usage_stats", "").format(
                tier=stats["tier"].upper(),
                ai_used=stats["ai_used_today"],
                ai_limit=ai_limit_text,
                pdf_used=stats["pdf_used_month"],
                pdf_limit=pdf_limit_text,
                img_used=stats["images_used_month"],
                img_limit=img_limit_text,
                expires_text=expires_text
            )

            keyboard = [
                [InlineKeyboardButton("🌟 Premium ($4.99/oy)", callback_data="buy_premium")],
                [InlineKeyboardButton("⭐ Pro ($14.99/oy)", callback_data="buy_pro")],
                [InlineKeyboardButton("🎁 Referral", callback_data="show_referral")],
                [InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]
            ]

            await safe_edit(query, usage_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
            conn.close()
        return

    if query.data == "show_referral":
        conn = get_db()
        if conn:
            ref_count = get_referral_stats(conn, user_id)

            # Mock bonuses (real implementation DB'da)
            bonuses = {
                "ai_requests": ref_count * 5,
                "pdf_bonus": ref_count * 2,
                "premium_days": 0  # 10 referral = 7 days premium
            }

            ref_text = get_referral_text(user_id, ref_count, bonuses, lang)
            keyboard = get_referral_share_keyboard(user_id, lang)

            await safe_edit(query, ref_text, reply_markup=keyboard, parse_mode="Markdown")
            conn.close()
        return

    if query.data.startswith("copy_ref_"):
        ref_code = query.data.replace("copy_ref_", "")
        bot_username = "MindMateAIBot"  # TODO: .env'dan olish
        ref_link = f"https://t.me/{bot_username}?start={ref_code}"

        await query.answer(f"✅ Link nusxalandi!\n\n{ref_link}", show_alert=True)
        return

    if query.data == "my_referral_bonuses":
        conn = get_db()
        if conn:
            ref_count = get_referral_stats(conn, user_id)
            text = f"""🎁 **Sizning Bonuslaringiz**

👥 Taklif qilgan do'stlar: {ref_count}

💰 **Olingan bonuslar:**
• +{ref_count * 5} ta AI so'rov
• +{ref_count * 2} ta PDF
• +{ref_count // 10 * 7} kun Premium

🎯 **Keyingi maqsad:**
{10 - (ref_count % 10)} ta do'st taklif qiling → 7 kun Premium! 🎉"""

            keyboard = [
                [InlineKeyboardButton("📤 Yana ulashish", callback_data="show_referral")],
                [InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]
            ]

            await safe_edit(query, text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
            conn.close()
        return

    if query.data in ["buy_premium", "buy_pro"]:
        tier = "premium" if query.data == "buy_premium" else "pro"
        tier_info = SUBSCRIPTION_TIERS[tier]
        price = tier_info["price"]

        # Telegram Stars pricing: 1 USD ≈ 50 Stars (adjust as needed)
        stars_price = int(price * 50)

        text = f"""💎 **{tier_info["name"]} Obuna**

💵 Narx: ${price}/oy ({stars_price} ⭐ Telegram Stars)

**Imkoniyatlar:**
"""
        for feature in tier_info["features"]:
            text += f"✅ {feature}\n"

        text += f"\n\n💳 **To'lov usullari:**\n\n"
        text += f"1️⃣ **Telegram Stars** - To'g'ridan-to'g'ri telegram orqali\n"
        text += f"2️⃣ **PayPal** - Xalqaro to'lov\n\n"
        text += f"To'lov usulini tanlang:"

        keyboard = [
            [InlineKeyboardButton("⭐ Telegram Stars", callback_data=f"pay_stars_{tier}")],
            [InlineKeyboardButton("💳 PayPal", callback_data=f"pay_paypal_{tier}")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="premium_menu")],
            [InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]
        ]

        await safe_edit(query, text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    # Telegram Stars payment
    if query.data.startswith("pay_stars_"):
        tier = query.data.replace("pay_stars_", "")
        tier_info = SUBSCRIPTION_TIERS[tier]
        price = tier_info["price"]
        stars_price = int(price * 50)

        try:
            # Send invoice for Telegram Stars
            await query.message.reply_invoice(
                title=f"{tier_info['name']} Obuna",
                description=f"MindMate {tier_info['name']} obunasi - 1 oy",
                payload=f"mindmate_{tier}_subscription_{user_id}",
                provider_token="",  # Empty for Telegram Stars
                currency="XTR",  # Telegram Stars currency code
                prices=[{"label": f"{tier_info['name']} - 1 oy", "amount": stars_price}],
                start_parameter=f"subscribe_{tier}",
                reply_markup=None
            )

            await query.answer("✅ To'lov oynasi yuborildi!")

        except Exception as e:
            logger.error(f"Telegram Stars to'lov xatosi: {e}")
            text = f"⚠️ **Xatolik yuz berdi!**\n\n{str(e)}\n\nIltimos, keyinroq qayta urinib ko'ring yoki PayPal orqali to'lang."
            keyboard = [
                [InlineKeyboardButton("💳 PayPal", callback_data=f"pay_paypal_{tier}")],
                [InlineKeyboardButton("🔙 Orqaga", callback_data="premium_menu")]
            ]
            await safe_edit(query, text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

        return

    # PayPal payment (placeholder)
    if query.data.startswith("pay_paypal_"):
        tier = query.data.replace("pay_paypal_", "")
        tier_info = SUBSCRIPTION_TIERS[tier]
        price = tier_info["price"]

        text = f"""💳 **PayPal To'lov**

💎 Obuna: {tier_info['name']}
💵 Narx: ${price}/oy

📧 **To'lov qilish uchun:**

1. PayPal: [your-paypal-email@example.com]
2. Summa: ${price} USD
3. Note: "MindMate {tier} - User ID: {user_id}"

✅ **To'lovdan keyin:**
Ushbu bot'ga screenshot yuboring va biz 24 soat ichida faollashtramiz!

⚠️ PayPal integratsiya tez orada avtomatik bo'ladi."""

        keyboard = [
            [InlineKeyboardButton("🔙 Orqaga", callback_data=f"buy_{tier}")],
            [InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]
        ]

        await safe_edit(query, text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    # === FINANCIAL MENU ===
    if query.data == "financial_menu":
        conn = get_db()
        if conn:
            # Check for quick expense shortcuts
            shortcuts = get_quick_expense_shortcuts(user_id, conn)

            if shortcuts:
                # Show quick shortcuts + main menu
                text = get_text(lang, "financial_coach_quick")
                keyboard_markup = get_expense_shortcuts_keyboard(shortcuts)
            else:
                # Standard menu
                keyboard = [
                    [InlineKeyboardButton("💸 Xarajat qo'shish", callback_data="add_expense"),
                     InlineKeyboardButton("💵 Daromad qo'shish", callback_data="add_income")],
                    [InlineKeyboardButton("📊 Oylik hisobot", callback_data="financial_report")],
                    [InlineKeyboardButton("💡 AI Maslahat", callback_data="financial_advice_start")],
                    [InlineKeyboardButton("📈 Investitsiya 💎", callback_data="investment_advice")],
                    [InlineKeyboardButton("🔄 Doimiy xarajat", callback_data="add_recurring_expense_start")],
                    [InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]
                ]
                text = get_text(lang, "financial_coach_menu")
                keyboard_markup = InlineKeyboardMarkup(keyboard)

            await safe_edit(query, text, reply_markup=keyboard_markup, parse_mode="Markdown")
            conn.close()
        return

    if query.data == "add_expense":
        context.user_data["waiting_for"] = "expense_amount"
        text = get_text(lang, "add_expense")
        await safe_edit(query, text, reply_markup=get_main_menu_button(lang), parse_mode="Markdown")
        return

    if query.data == "add_income":
        context.user_data["waiting_for"] = "income_amount"
        text = get_text(lang, "add_income")
        await safe_edit(query, text, reply_markup=get_main_menu_button(lang), parse_mode="Markdown")
        return

    if query.data == "financial_report":
        conn = get_db()
        if conn:
            summary = get_monthly_summary(conn, user_id)

            breakdown = ""
            for cat, amt in summary["expenses_by_category"].items():
                percentage = (amt / summary["total_expenses"] * 100) if summary["total_expenses"] > 0 else 0
                breakdown += f"• {cat}: {amt:,.0f} so'm ({percentage:.1f}%)\n"

            if not breakdown:
                breakdown = "Hali xarajatlar yo'q"

            report_text = f"""📊 **Oylik Moliyaviy Hisobot**

💵 Daromad: {summary['total_income']:,.0f} so'm
💸 Xarajat: {summary['total_expenses']:,.0f} so'm
💰 Balans: {summary['balance']:,.0f} so'm

📈 **Xarajatlar taqsimoti:**
{breakdown}

💡 Tahlil uchun "AI Maslahat" tugmasini bosing."""

            keyboard = [
                [InlineKeyboardButton("💡 AI Tahlil", callback_data="analyze_spending")],
                [InlineKeyboardButton("🔙 Orqaga", callback_data="financial_menu")],
                [InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]
            ]

            await safe_edit(query, report_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
            conn.close()
        return

    if query.data == "analyze_spending":
        conn = get_db()
        if conn:
            await query.message.reply_text("🔍 Xarajatlaringizni tahlil qilyapman...")
            analysis = await analyze_spending_habits(user_id, conn, lang)
            await query.message.reply_text(analysis, parse_mode="Markdown")
            conn.close()
        return

    if query.data == "financial_advice_start":
        context.user_data["waiting_for"] = "financial_question"
        text = get_text(lang, "financial_advice_prompt")
        await safe_edit(query, text, reply_markup=get_main_menu_button(lang), parse_mode="Markdown")
        return

    if query.data == "investment_advice":
        # Check if user is premium
        conn = get_db()
        if conn:
            subscription = get_user_subscription(conn, user_id)
            tier = subscription.get("tier", "free")

            if tier == "free":
                # Show disclaimer and premium requirement
                text = get_investment_disclaimer() + "\n\n💎 **Investitsiya maslahati Premium va Pro foydalanuvchilar uchun!**\n\n3 ta bepul sinov maslahati mavjud."
                keyboard = [
                    [InlineKeyboardButton("✅ Bepul sinov (3ta)", callback_data="investment_disclaimer_free")],
                    [InlineKeyboardButton("💎 Premium xarid qilish", callback_data="buy_premium")],
                    [InlineKeyboardButton("🔙 Orqaga", callback_data="financial_menu")]
                ]
            else:
                # Show disclaimer only
                text = get_investment_disclaimer()
                keyboard = [
                    [InlineKeyboardButton("✅ Tushunarli, davom etamiz", callback_data="investment_disclaimer_accept")],
                    [InlineKeyboardButton("🔙 Orqaga", callback_data="financial_menu")]
                ]

            await safe_edit(query, text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
            conn.close()
        return

    if query.data == "investment_disclaimer_accept":
        context.user_data["waiting_for"] = "investment_amount"
        text = get_text(lang, "investment_advice_amount")
        await safe_edit(query, text, reply_markup=get_main_menu_button(lang), parse_mode="Markdown")
        return

    if query.data == "investment_disclaimer_free":
        # Free tier - check usage limit
        conn = get_db()
        if conn:
            # Check investment advice usage
            cur = conn.cursor()
            cur.execute("""
                SELECT COUNT(*) FROM usage_stats
                WHERE user_id = %s AND feature = 'investment_advice'
                AND used_at >= DATE_TRUNC('month', CURRENT_DATE)
            """, (user_id,))
            usage_count = cur.fetchone()[0]
            cur.close()

            if usage_count >= 3:
                text = "⚠️ Siz bu oyda 3 ta bepul sinov maslahatidan foydalandingiz.\n\n💎 Premium xarid qiling!"
                keyboard = [
                    [InlineKeyboardButton("💎 Premium", callback_data="buy_premium")],
                    [InlineKeyboardButton("🔙 Orqaga", callback_data="financial_menu")]
                ]
                await safe_edit(query, text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
            else:
                context.user_data["waiting_for"] = "investment_amount"
                text = f"📈 **Investitsiya Maslahati** (Bepul: {3 - usage_count} qoldi)\n\nInvestitsiya qilmoqchi bo'lgan summangizni kiriting:"
                await safe_edit(query, text, reply_markup=get_main_menu_button(lang), parse_mode="Markdown")

            conn.close()
        return

    # Quick expense shortcuts - one-tap adding
    if query.data.startswith("quick_exp_"):
        parts = query.data.split("_")
        category = parts[2]
        amount = float(parts[3])

        conn = get_db()
        if conn:
            add_expense(conn, user_id, amount, category, f"Tez xarajat: {category}")
            text = f"✅ **Xarajat qo'shildi!**\n\n🍽️ Kategoriya: {category.title()}\n💰 Summa: {amount:,.0f} so'm"

            keyboard = [
                [InlineKeyboardButton("📊 Hisobot", callback_data="financial_report")],
                [InlineKeyboardButton("💰 Moliya", callback_data="financial_menu")],
                [InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]
            ]

            await safe_edit(query, text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
            conn.close()
        return

    # Add recurring expense
    if query.data == "add_recurring_expense_start":
        context.user_data["waiting_for"] = "recurring_expense_amount"
        text = get_text(lang, "recurring_expense")
        await safe_edit(query, text, reply_markup=get_main_menu_button(lang), parse_mode="Markdown")
        return

    # === MY PROFILE SUBMENUS ===

    if query.data == "stats":
        conn = get_db()
        if conn:
            # Get comprehensive stats
            subscription = get_user_subscription(conn, user_id)
            tasks_completed = get_user_tasks(conn, user_id, include_completed=True)
            completed_count = sum(1 for t in tasks_completed if t.get("completed"))
            financial_summary = get_monthly_summary(conn, user_id)

            text = f"""📊 **Sizning Statistikangiz**

💎 **Obuna:** {subscription.get('tier', 'free').upper()}

📝 **Vazifalar:**
• Bajarilgan: {completed_count}
• Jami: {len(tasks_completed)}

💰 **Moliya (bu oy):**
• Daromad: {financial_summary.get('total_income', 0):,.0f} so'm
• Xarajat: {financial_summary.get('total_expenses', 0):,.0f} so'm
• Balans: {financial_summary.get('balance', 0):,.0f} so'm

🎯 **Yutuqlar:** Coming soon!"""

            keyboard = [
                [InlineKeyboardButton("🔙 Orqaga", callback_data="my_profile")],
                [InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]
            ]

            await safe_edit(query, text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
            conn.close()
        return

    if query.data == "goals":
        text = get_text(lang, "your_goals")
        keyboard = [
            [InlineKeyboardButton("🔙 Orqaga", callback_data="my_profile")],
            [InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]
        ]
        await safe_edit(query, text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    if query.data == "achievements":
        text = get_text(lang, "achievements")
        keyboard = [
            [InlineKeyboardButton("🔙 Orqaga", callback_data="my_profile")],
            [InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]
        ]
        await safe_edit(query, text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    if query.data == "progress":
        text = get_text(lang, "progress")
        keyboard = [
            [InlineKeyboardButton("🔙 Orqaga", callback_data="my_profile")],
            [InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]
        ]
        await safe_edit(query, text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    # === SETTINGS SUBMENUS ===

    if query.data == "notifications":
        text = get_text(lang, "notifications")
        keyboard = [
            [InlineKeyboardButton("🔙 Orqaga", callback_data="settings_menu")],
            [InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]
        ]
        await safe_edit(query, text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    if query.data == "reset_confirm":
        text = get_text(lang, "reset_history")
        keyboard = [
            [InlineKeyboardButton("✅ Ha, tozalash", callback_data="reset_history_yes")],
            [InlineKeyboardButton("❌ Yo'q", callback_data="settings_menu")]
        ]
        await safe_edit(query, text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    if query.data == "reset_history_yes":
        # Delete chat history but keep other data
        conn = get_db()
        if conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM memories WHERE user_id = %s AND key IN ('recent_messages', 'conversation_context')", (user_id,))
            conn.commit()
            cur.close()
            conn.close()

        text = get_text(lang, "history_cleared")
        await safe_edit(query, text, reply_markup=get_main_menu_button(lang), parse_mode="Markdown")
        return

    if query.data == "help":
        text = get_text(lang, "help_text")
        keyboard = [
            [InlineKeyboardButton("🔙 Orqaga", callback_data="settings_menu")],
            [InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]
        ]
        await safe_edit(query, text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    # === HEALTH MENU SUBMENUS ===

    if query.data == "health_ai":
        context.user_data["mode"] = "health_ai"
        text = get_text(lang, "health_ai")
        await safe_edit(query, text, reply_markup=get_main_menu_button(lang), parse_mode="Markdown")
        return

    # === PRODUCTIVITY MENU ===
    if query.data == "productivity_menu":
        keyboard = [
            [InlineKeyboardButton("📝 Vazifa qo'shish", callback_data="add_task_start"),
             InlineKeyboardButton("📋 Vazifalarim", callback_data="view_tasks")],
            [InlineKeyboardButton("📅 Kunlik reja", callback_data="create_daily_plan_start")],
            [InlineKeyboardButton("🎯 Fokus sessiya", callback_data="start_focus_25")],
            [InlineKeyboardButton("📊 Productivity hisobot", callback_data="productivity_report")],
            [InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]
        ]
        text = get_text(lang, "productivity_coach_menu")
        await safe_edit(query, text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    if query.data == "add_task_start":
        context.user_data["waiting_for"] = "task_title"
        text = get_text(lang, "add_task")
        await safe_edit(query, text, reply_markup=get_main_menu_button(lang), parse_mode="Markdown")
        return

    if query.data == "view_tasks":
        conn = get_db()
        if conn:
            tasks = get_user_tasks(conn, user_id, include_completed=False)

            if not tasks:
                text = get_text(lang, "no_tasks")
                keyboard = [
                    [InlineKeyboardButton("➕ Vazifa qo'shish", callback_data="add_task_start")],
                    [InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]
                ]
            else:
                text = get_text(lang, "your_tasks") + "\n\n"
                keyboard = []

                for i, task in enumerate(tasks[:10], 1):
                    priority_emoji = {"urgent": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(task["priority"], "⚪")
                    text += f"{i}. {priority_emoji} {task['title']}\n"
                    keyboard.append([
                        InlineKeyboardButton(f"✅ {i}. {task['title'][:20]}...", callback_data=f"complete_task_{task['id']}")
                    ])

                keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="productivity_menu")])
                keyboard.append([InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")])

            await safe_edit(query, text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
            conn.close()
        return

    if query.data.startswith("complete_task_"):
        task_id = int(query.data.split("_")[2])
        conn = get_db()
        if conn:
            success = complete_task(conn, task_id)
            if success:
                await query.answer("🎉 Vazifa bajarildi! Tabriklaymiz!", show_alert=True)
            conn.close()
        # Refresh task list
        await button_callback(update, context)  # Recursively call to refresh
        return

    if query.data == "create_daily_plan_start":
        conn = get_db()
        if conn:
            await query.message.reply_text("📅 Bugun uchun reja yaratyapman...")
            plan = await create_daily_plan(user_id, conn, work_hours=8, lang=lang)
            await query.message.reply_text(f"📅 **Kunlik Reja:**\n\n{plan}", parse_mode="Markdown")
            conn.close()
        return

    if query.data == "start_focus_25":
        conn = get_db()
        if conn:
            session_id = start_focus_session(conn, user_id, duration=25)
            text = """🎯 **Fokus Sessiyasi Boshlandi!**

⏱️ 25 minut

💡 **Qoidalar:**
• Telefon va ijtimoiy tarmoqlarni yoping
• Faqat bitta vazifaga e'tibor bering
• 25 minut tugagach 5 minut dam oling

Muvaffaqiyat! 💪"""

            keyboard = [
                [InlineKeyboardButton("✅ Tugatdim", callback_data=f"end_focus_{session_id}")],
                [InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]
            ]

            await safe_edit(query, text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
            conn.close()
        return

    if query.data.startswith("end_focus_"):
        session_id = int(query.data.split("_")[2])
        conn = get_db()
        if conn:
            complete_focus_session(conn, session_id)
            text = """🎉 **Fokus Sessiyasi Tugadi!**

Ajoyib! Siz 25 minut to'liq fokusda ishladingiz!

☕ **5 daqiqa dam oling:**
• Cho'zilib oling
• Suvdan iching
• Ko'zlaringizni dam oldiring

Keyingi sessiyaga tayyormisiz?"""

            keyboard = [
                [InlineKeyboardButton("🔁 Yana 25 min", callback_data="start_focus_25")],
                [InlineKeyboardButton("📊 Hisobot", callback_data="productivity_report")],
                [InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]
            ]

            await safe_edit(query, text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
            conn.close()
        return

    if query.data == "productivity_report":
        conn = get_db()
        if conn:
            await query.message.reply_text("📊 Unumdorlikni tahlil qilyapman...")
            report = await analyze_productivity(user_id, conn, days=7, lang=lang)
            await query.message.reply_text(f"📊 **Unumdorlik Hisoboti:**\n\n{report}", parse_mode="Markdown")
            conn.close()
        return

    # === FINANCIAL CALLBACKS ===
    if query.data.startswith("excat_"):
        category = query.data.replace("excat_", "")
        amount = context.user_data.get("expense_amount", 0)

        conn = get_db()
        if conn and amount > 0:
            add_expense(conn, user_id, amount, category)
            await query.answer("✅ Xarajat saqlandi!", show_alert=True)
            await query.message.reply_text(
                f"✅ Xarajat saqlandi: {amount:,.0f} so'm ({category})",
                reply_markup=get_main_menu_button(lang)
            )
            conn.close()

        context.user_data["waiting_for"] = None
        context.user_data["expense_amount"] = None
        return

    if query.data.startswith("risk_"):
        risk_level = query.data.replace("risk_", "")
        amount = context.user_data.get("investment_amount", 0)

        if amount > 0:
            await query.message.reply_text("📊 Investitsiya maslahatini tayyorlamoqdaman...")
            advice = await get_investment_advice(amount, risk_level, "1 yil", lang)
            await query.message.reply_text(f"📈 **Investitsiya Maslahati:**\n\n{advice}", parse_mode="Markdown")

        context.user_data["waiting_for"] = None
        context.user_data["investment_amount"] = None
        return

    # Translation language selection
    if query.data.startswith("tlang_"):
        target_lang = query.data.replace("tlang_", "")
        text_to_translate = context.user_data.get("translate_text", "")
        if text_to_translate:
            await query.message.reply_text("🌐 Tarjima qilinmoqda...")
            translation = await translate_text(text_to_translate, target_lang)
            if translation:
                await query.message.reply_text(f"✅ **Tarjima:**\n\n{translation}", parse_mode="Markdown")
            else:
                await query.message.reply_text("⚠️ Tarjima qilishda xatolik.", reply_markup=get_main_menu_button(lang))
        context.user_data["waiting_for"] = None
        context.user_data["translate_text"] = None
        return

# === PAYMENT HANDLERS ===

async def pre_checkout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pre-checkout validation for Telegram Stars payments"""
    query = update.pre_checkout_query

    # Always approve for now (add validation logic if needed)
    await query.answer(ok=True)


async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle successful payment"""
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)

    # Get payment info
    payment_info = update.message.successful_payment
    payload = payment_info.invoice_payload

    try:
        # Parse payload: "mindmate_premium_subscription_123456"
        parts = payload.split("_")
        tier = parts[1]  # premium or pro

        # Activate subscription
        conn = get_db()
        if conn:
            cur = conn.cursor()

            # Update or insert subscription
            cur.execute("""
                INSERT INTO subscriptions (user_id, tier, expires_at)
                VALUES (%s, %s, CURRENT_DATE + INTERVAL '30 days')
                ON CONFLICT (user_id)
                DO UPDATE SET
                    tier = EXCLUDED.tier,
                    expires_at = EXCLUDED.expires_at,
                    updated_at = CURRENT_TIMESTAMP
            """, (user_id, tier))

            # Log transaction
            cur.execute("""
                INSERT INTO transactions (user_id, amount, currency, status, payload)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, payment_info.total_amount, payment_info.currency, "completed", payload))

            conn.commit()
            cur.close()
            conn.close()

        tier_info = SUBSCRIPTION_TIERS.get(tier, SUBSCRIPTION_TIERS["premium"])

        success_text = f"""🎉 **Payment Successful!**

✅ {tier_info['name']} subscription activated!

💎 **Your Benefits:**
"""
        for feature in tier_info["features"]:
            success_text += f"✅ {feature}\n"

        success_text += f"\n⏰ Valid until: {(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')}\n\n🚀 Enjoy unlimited access!"

        await update.message.reply_text(
            success_text,
            reply_markup=get_main_menu_button(lang),
            parse_mode="Markdown"
        )

    except Exception as e:
        logger.error(f"Payment processing error: {e}")
        await update.message.reply_text(
            "✅ Payment received! Your subscription will be activated within 5 minutes.",
            reply_markup=get_main_menu_button(lang)
        )


# === MESSAGE HANDLER ===

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text
    lang = get_user_lang(user_id)

    # Input validation: check message length
    if not user_message or len(user_message) > 4000:
        await update.message.reply_text(
            get_text(lang, "error") if len(user_message) > 4000 else "⚠️ Xabar bo'sh bo'lishi mumkin emas.",
            reply_markup=get_main_menu_button(lang)
        )
        return

    waiting_for = context.user_data.get("waiting_for")

    # Journal
    if waiting_for == "journal":
        save_journal(user_id, user_message)
        context.user_data["waiting_for"] = None
        text = get_text(lang, "journal_saved") + "\n\n💭 Yozganlaringizni eslab qolaman."
        await update.message.reply_text(text, reply_markup=get_main_menu_button(lang))
        return

    # PDF Creation
    if waiting_for == "pdf_title":
        context.user_data["pdf_title"] = user_message
        context.user_data["waiting_for"] = "pdf_content"
        await update.message.reply_text("✍️ Endi matnni kiriting (har bir paragraf alohida qatorda):", reply_markup=get_main_menu_button(lang))
        return

    if waiting_for == "pdf_content":
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="upload_document")
        title = context.user_data.get("pdf_title", "Document")
        pdf_buffer = create_pdf_document(title, user_message)
        if pdf_buffer:
            await update.message.reply_document(
                document=pdf_buffer,
                filename=f"{title}.pdf",
                caption="📄 PDF hujjatingiz tayyor!"
            )
        else:
            await update.message.reply_text("⚠️ Xatolik yuz berdi. Qaytadan urinib ko'ring.", reply_markup=get_main_menu_button(lang))
        context.user_data["waiting_for"] = None
        context.user_data["pdf_title"] = None
        return

    # Presentation Creation
    if waiting_for == "ppt_title":
        context.user_data["ppt_title"] = user_message
        context.user_data["waiting_for"] = "ppt_slides"
        await update.message.reply_text("📊 Slayd mazmunini kiriting (har bir slayd uchun: 'SLAYD: sarlavha\nmatn'):", reply_markup=get_main_menu_button(lang))
        return

    if waiting_for == "ppt_slides":
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="upload_document")
        title = context.user_data.get("ppt_title", "Presentation")
        # Parse slides
        slides_data = []
        slides_raw = user_message.split("SLAYD:")
        for slide_text in slides_raw[1:]:  # Skip first empty
            lines = slide_text.strip().split('\n', 1)
            slide_title = lines[0].strip() if lines else "Slide"
            slide_content = lines[1].strip() if len(lines) > 1 else ""
            slides_data.append({"title": slide_title, "content": slide_content})

        if not slides_data:
            # Auto-generate simple slides from text
            paragraphs = user_message.split('\n\n')
            for i, para in enumerate(paragraphs[:10], 1):
                slides_data.append({"title": f"Slayd {i}", "content": para})

        ppt_buffer = create_presentation(title, slides_data)
        if ppt_buffer:
            await update.message.reply_document(
                document=ppt_buffer,
                filename=f"{title}.pptx",
                caption="📊 Prezentatsiya tayyor!"
            )
        else:
            await update.message.reply_text("⚠️ Xatolik yuz berdi. Qaytadan urinib ko'ring.", reply_markup=get_main_menu_button(lang))
        context.user_data["waiting_for"] = None
        context.user_data["ppt_title"] = None
        return

    # Resume Creation
    if waiting_for == "resume_name":
        context.user_data["resume_name"] = user_message
        context.user_data["waiting_for"] = "resume_details"
        await update.message.reply_text("📋 Qisqacha ma'lumotlaringizni kiriting:\n\nEmail:\nTelefon:\nTajriba:\nKo'nikmalar:", reply_markup=get_main_menu_button(lang))
        return

    if waiting_for == "resume_details":
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="upload_document")
        name = context.user_data.get("resume_name", "Name")
        resume_data = {"name": name, "summary": user_message, "experience": [], "skills": [], "education": []}
        pdf_buffer = create_resume_pdf(resume_data)
        if pdf_buffer:
            await update.message.reply_document(
                document=pdf_buffer,
                filename=f"Resume_{name}.pdf",
                caption="📋 Rezyume tayyor!"
            )
        else:
            await update.message.reply_text("⚠️ Xatolik yuz berdi. Qaytadan urinib ko'ring.", reply_markup=get_main_menu_button(lang))
        context.user_data["waiting_for"] = None
        context.user_data["resume_name"] = None
        return

    # AI Image Generation
    if waiting_for == "image_prompt":
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="upload_photo")
        await update.message.reply_text("🎨 Rasm yaratilmoqda... Kuting...")
        image_url = await generate_image(user_message)
        if image_url:
            await update.message.reply_photo(photo=image_url, caption="✅ Rasm tayyor!")
        else:
            await update.message.reply_text("⚠️ Rasm yaratishda xatolik. Qaytadan urinib ko'ring.", reply_markup=get_main_menu_button(lang))
        context.user_data["waiting_for"] = None
        return

    # Translation
    if waiting_for == "translate_text":
        context.user_data["translate_text"] = user_message
        context.user_data["waiting_for"] = "translate_lang"
        keyboard = [
            [InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="tlang_uz"),
             InlineKeyboardButton("🇷🇺 Русский", callback_data="tlang_ru")],
            [InlineKeyboardButton("🇬🇧 English", callback_data="tlang_en"),
             InlineKeyboardButton("🇹🇷 Türkçe", callback_data="tlang_tr")],
            [InlineKeyboardButton("🇸🇦 العربية", callback_data="tlang_ar"),
             InlineKeyboardButton("🇨🇳 中文", callback_data="tlang_zh")]
        ]
        await update.message.reply_text("🌍 Qaysi tilga tarjima qilish kerak?", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # Code Generation
    if waiting_for == "code_description":
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        code = await generate_code(user_message)
        if code:
            await update.message.reply_text(f"👨‍💻 **Kod:**\n\n{code}", parse_mode="Markdown")
        else:
            await update.message.reply_text("⚠️ Kod yaratishda xatolik.", reply_markup=get_main_menu_button(lang))
        context.user_data["waiting_for"] = None
        return

    # Recipe
    if waiting_for == "recipe_name":
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        recipe = await find_recipe(user_message, lang)
        if recipe:
            await update.message.reply_text(f"🍳 **Retsept:**\n\n{recipe}", parse_mode="Markdown")
        else:
            await update.message.reply_text("⚠️ Retsept topilmadi.", reply_markup=get_main_menu_button(lang))
        context.user_data["waiting_for"] = None
        return

    # Travel Planning
    if waiting_for == "travel_destination":
        context.user_data["travel_dest"] = user_message
        context.user_data["waiting_for"] = "travel_days"
        await update.message.reply_text("📅 Necha kunlik sayohat?")
        return

    if waiting_for == "travel_days":
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        dest = context.user_data.get("travel_dest", "")
        try:
            days = int(user_message)
            plan = await create_travel_plan(dest, days, lang=lang)
            if plan:
                await update.message.reply_text(f"✈️ **Sayohat Rejasi:**\n\n{plan}", parse_mode="Markdown")
            else:
                await update.message.reply_text("⚠️ Reja yaratishda xatolik.", reply_markup=get_main_menu_button(lang))
        except:
            await update.message.reply_text("⚠️ Kun sonini raqamda kiriting.")
        context.user_data["waiting_for"] = None
        context.user_data["travel_dest"] = None
        return

    # Study Material
    if waiting_for == "study_topic":
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        material = await create_study_material(user_message, lang=lang)
        if material:
            await update.message.reply_text(f"📚 **O'quv Materiali:**\n\n{material}", parse_mode="Markdown")
        else:
            await update.message.reply_text("⚠️ Material yaratishda xatolik.", reply_markup=get_main_menu_button(lang))
        context.user_data["waiting_for"] = None
        return

    # Business Idea
    if waiting_for == "business_industry":
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        industry = None if user_message.lower() in ["ixtiyoriy", "any", "none"] else user_message
        idea = await generate_business_idea(industry, lang)
        if idea:
            await update.message.reply_text(f"💼 **Biznes G'oyasi:**\n\n{idea}", parse_mode="Markdown")
        else:
            await update.message.reply_text("⚠️ G'oya yaratishda xatolik.", reply_markup=get_main_menu_button(lang))
        context.user_data["waiting_for"] = None
        return

    # Email Writing
    if waiting_for == "email_purpose":
        context.user_data["email_purpose"] = user_message
        context.user_data["waiting_for"] = "email_points"
        await update.message.reply_text("📝 Asosiy fikrlarni kiriting:")
        return

    if waiting_for == "email_points":
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        purpose = context.user_data.get("email_purpose", "")
        email = await write_email(purpose, "recipient", user_message, lang)
        if email:
            await update.message.reply_text(f"✉️ **Email:**\n\n{email}", parse_mode="Markdown")
        else:
            await update.message.reply_text("⚠️ Email yozishda xatolik.", reply_markup=get_main_menu_button(lang))
        context.user_data["waiting_for"] = None
        context.user_data["email_purpose"] = None
        return

    # === FINANCIAL INPUTS ===
    if waiting_for == "expense_amount":
        try:
            amount = float(user_message.replace(",", "").replace(" ", ""))
            context.user_data["expense_amount"] = amount
            context.user_data["waiting_for"] = "expense_category"

            keyboard = [
                [InlineKeyboardButton("🍽️ Ovqat", callback_data="excat_food"),
                 InlineKeyboardButton("🚗 Transport", callback_data="excat_transport")],
                [InlineKeyboardButton("🏠 Uy-joy", callback_data="excat_housing"),
                 InlineKeyboardButton("💡 Kommunal", callback_data="excat_utilities")],
                [InlineKeyboardButton("🏥 Sog'liq", callback_data="excat_healthcare"),
                 InlineKeyboardButton("📚 Ta'lim", callback_data="excat_education")],
                [InlineKeyboardButton("🎬 O'yin-kulgi", callback_data="excat_entertainment"),
                 InlineKeyboardButton("🛍️ Xaridlar", callback_data="excat_shopping")],
                [InlineKeyboardButton("📦 Boshqa", callback_data="excat_other")]
            ]

            await update.message.reply_text(
                f"💸 Summa: {amount:,.0f} so'm\n\n📂 Kategoriyani tanlang:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except:
            await update.message.reply_text("⚠️ Summa raqamda kiriting (masalan: 50000)")
        return

    if waiting_for == "income_amount":
        try:
            amount = float(user_message.replace(",", "").replace(" ", ""))
            conn = get_db()
            if conn:
                add_income(conn, user_id, amount, "salary", "Daromad")
                await update.message.reply_text(
                    f"✅ Daromad saqlandi: {amount:,.0f} so'm",
                    reply_markup=get_main_menu_button(lang)
                )
                conn.close()
            context.user_data["waiting_for"] = None
        except:
            await update.message.reply_text("⚠️ Summa raqamda kiriting (masalan: 1000000)")
        return

    if waiting_for == "financial_question":
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        conn = get_db()
        if conn:
            advice = await get_financial_advice(user_id, conn, user_message, lang)
            await update.message.reply_text(f"💡 **AI Maslahat:**\n\n{advice}", parse_mode="Markdown")
            conn.close()
        context.user_data["waiting_for"] = None
        return

    if waiting_for == "investment_amount":
        try:
            amount = float(user_message.replace(",", "").replace(" ", ""))
            context.user_data["investment_amount"] = amount
            context.user_data["waiting_for"] = "investment_risk"

            keyboard = [
                [InlineKeyboardButton("🟢 Past", callback_data="risk_low")],
                [InlineKeyboardButton("🟡 O'rta", callback_data="risk_medium")],
                [InlineKeyboardButton("🔴 Yuqori", callback_data="risk_high")]
            ]

            await update.message.reply_text(
                "📊 Risk darajasini tanlang:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except:
            await update.message.reply_text("⚠️ Summa raqamda kiriting")
        return

    # === PRODUCTIVITY INPUTS ===
    if waiting_for == "task_title":
        conn = get_db()
        if conn:
            task_id = add_task(conn, user_id, user_message, priority="medium")
            await update.message.reply_text(
                f"✅ Vazifa qo'shildi: {user_message}",
                reply_markup=get_main_menu_button(lang)
            )
            conn.close()
        context.user_data["waiting_for"] = None
        return

    # Default: AI Chat
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
    
    # Command handlers
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

    # Payment handlers (Telegram Stars)
    from telegram.ext import PreCheckoutQueryHandler
    app.add_handler(PreCheckoutQueryHandler(pre_checkout_callback))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))

    # Callback and message handlers
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("✅ MindMate JARVIS bot ishga tushdi!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()