import os
import logging
import psycopg2
import json
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from openai import OpenAI
from languages import get_text, get_mood_response, TRANSLATIONS
from fitness import get_workout_text, get_workout_buttons, get_workout_done, get_workout_stats_label
from healer import get_healer_prompt, get_healer_buttons
from ai_brain import get_master_prompt

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# OpenAI client - faqat API key mavjud bo'lsa yaratish
client = None
if OPENAI_API_KEY:
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
    
    # Users jadvali - kengaytirilgan profil
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            language TEXT DEFAULT 'uz',
            profile_data JSONB DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Kayfiyat tarixi
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
    
    # Kundalik
    cur.execute('''
        CREATE TABLE IF NOT EXISTS journals (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            text TEXT,
            ai_analysis TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Suhbat tarixi - MUHIM!
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
    
    # Mashqlar
    cur.execute('''
        CREATE TABLE IF NOT EXISTS workouts (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            workout_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Shifokor seanslar
    cur.execute('''
        CREATE TABLE IF NOT EXISTS healer_sessions (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            problem_type TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Foydalanuvchi xotiralari - JARVIS uchun
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
            UNIQUE(user_id, memory_key)
        )
    ''')
    
    conn.commit()
    cur.close()
    conn.close()
    logger.info("✅ Database initialized with JARVIS memory system")

# === USER FUNCTIONS ===

def save_user(user_id, username, full_name=None, lang="uz"):
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
        INSERT INTO user_memories (user_id, memory_type, memory_key, memory_value, importance, updated_at)
        VALUES (%s, %s, %s, %s, %s, NOW())
        ON CONFLICT (user_id, memory_key) DO UPDATE SET
            memory_value = EXCLUDED.memory_value,
            importance = EXCLUDED.importance,
            updated_at = NOW()
    ''', (user_id, memory_type, key, value, importance))
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
    
    # Kayfiyat tendensiyasini xotiraga saqlash
    save_memory(user_id, "mood", "last_mood", f"{score}/5", importance=1)

def save_journal(user_id, text):
    conn = get_db()
    if conn is None:
        return
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
    
    # Muammoni xotiraga saqlash
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

# === SAFE EDIT ===
def escape_markdown(text):
    """Markdown maxsus belgilaridan qochish"""
    if not text:
        return text
    # Markdown maxsus belgilari
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text

async def safe_edit(query, text, reply_markup=None, parse_mode=None):
    try:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
    except Exception as e:
        logger.error(f"Edit xato: {e}")
        try:
            # Markdown xato bo'lsa, parse_mode siz yuborish
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=None)
        except:
            try:
                await query.message.reply_text(text, reply_markup=reply_markup, parse_mode=None)
            except:
                pass

# === AI BRAIN (JARVIS) ===

async def extract_and_save_memories(user_id, user_message, ai_response, lang):
    """AI javobidan muhim ma'lumotlarni ajratib, xotiraga saqlash"""
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
        
        # JSON ni parse qilish
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
    if not client:
        return "⚠️ AI xizmati hozirda mavjud emas. Iltimos .env faylni sozlang va OPENAI_API_KEY ni qo'shing."

    lang = get_user_lang(user_id)

    # Foydalanuvchi haqida ma'lumotlar
    profile = get_user_profile(user_id)
    memories = get_user_memories(user_id)
    memories_text = format_memories_for_ai(memories)
    
    # Suhbat tarixi
    conversations = get_conversations(user_id, limit=20)
    important_convs = get_important_conversations(user_id, limit=5)
    
    # Kayfiyat tarixi
    mood_history = get_mood_history(user_id, limit=5)
    mood_text = ""
    if mood_history:
        mood_text = "\n📊 KAYFIYAT TARIXI:\n"
        for m in mood_history:
            mood_text += f"- {m['date'].strftime('%d.%m')}: {m['score']}/5\n"
    
    # System prompt tanlash
    if mode == "healer":
        base_prompt = get_healer_prompt(lang)
    else:
        base_prompt = get_master_prompt(lang, memories_text, "")
    
    # To'liq kontekst
    full_context = f"""{base_prompt}

{memories_text}
{mood_text}

📝 MUHIM ESLATMALAR:
- Foydalanuvchi ismi: {profile.get('full_name') or profile.get('username') or 'noma\'lum'}
- Bot bilan: {profile.get('member_since', 'yangi')}dan beri

Har bir javobda:
1. Oldingi ma'lumotlardan foydalaning
2. Shaxsiylashtirilgan javob bering
3. Samimiy va foydali bo'ling"""
    
    messages = [{"role": "system", "content": full_context}]
    
    # Muhim suhbatlar
    for conv in important_convs:
        messages.append(conv)
    
    # Oxirgi suhbatlar
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
        
        # Suhbatni saqlash
        importance = 2 if mode == "healer" else 1
        save_conversation(user_id, "user", message, mode, importance)
        save_conversation(user_id, "assistant", ai_message, mode, importance)
        
        # Xotiradan muhim ma'lumotlarni ajratish (background)
        await extract_and_save_memories(user_id, message, ai_message, lang)
        
        return ai_message
    except Exception as e:
        logger.error(f"OpenAI xatosi: {e}")
        return get_text(lang, "error")

# === COMMANDS ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    save_user(user.id, user.username, full_name)
    lang = get_user_lang(user.id)
    context.user_data["mode"] = "normal"
    
    # Qaytib kelgan foydalanuvchini tanish
    memories = get_user_memories(user.id)
    name = None
    for m in memories:
        if m["key"] == "name":
            name = m["value"]
            break
    
    if name:
        welcome = f"🌟 Xush kelibsiz, **{name}**! Sizni yana ko'rganimdan xursandman! Bugun qanday yordam bera olaman?"
    else:
        welcome = get_text(lang, "welcome")
    
    keyboard = [
        [InlineKeyboardButton("💬 Suhbat", callback_data="chat"),
         InlineKeyboardButton("🌿 Shifokor", callback_data="healer")],
        [InlineKeyboardButton(get_text(lang, "btn_mood"), callback_data="mood"),
         InlineKeyboardButton(get_text(lang, "btn_journal"), callback_data="journal")],
        [InlineKeyboardButton(get_text(lang, "btn_meditate"), callback_data="meditate"),
         InlineKeyboardButton("💪 Fitness", callback_data="fitness")],
        [InlineKeyboardButton(get_text(lang, "btn_stats"), callback_data="stats"),
         InlineKeyboardButton("🌍 Til", callback_data="lang")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome, reply_markup=reply_markup, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_lang(update.effective_user.id)
    help_text = """
🤖 **MindMate - Sizning JARVIS'ingiz**

Men sizning shaxsiy AI yordamchingizman. Sizni tinglayman, tushunaman va yordam beraman.

**Imkoniyatlar:**
💬 **Suhbat** - Men bilan istalgan mavzuda gaplashing
🌿 **Shifokor** - Tabiiy usullar bilan yordam
😊 **Kayfiyat** - Har kungi kayfiyatingizni kuzating
📝 **Kundalik** - Fikrlaringizni yozing
🧘 **Meditatsiya** - Tinchlanish mashqlari
💪 **Fitness** - Sog'lom turmush mashqlari

**Men nimalarni eslab qolaman:**
- Sizning ismingiz va qiziqishlaringiz
- Oldingi muammolaringiz va yechimlar
- Kayfiyat tarixingiz
- Sizga mos maslahatlar

Shunchaki yozing - men sizni tushunaman! ❤️
    """
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def mood_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_lang(update.effective_user.id)
    keyboard = [
        [InlineKeyboardButton("😄 Zo'r (5)", callback_data="mood_5"),
         InlineKeyboardButton("🙂 Yaxshi (4)", callback_data="mood_4")],
        [InlineKeyboardButton("😐 Normal (3)", callback_data="mood_3"),
         InlineKeyboardButton("😔 Yomon (2)", callback_data="mood_2")],
        [InlineKeyboardButton("😢 Juda yomon (1)", callback_data="mood_1")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(get_text(lang, "mood_ask"), reply_markup=reply_markup)

async def journal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_lang(update.effective_user.id)
    context.user_data["waiting_for"] = "journal"
    await update.message.reply_text(get_text(lang, "journal_ask"), parse_mode="Markdown")

async def meditate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_lang(update.effective_user.id)
    keyboard = [
        [InlineKeyboardButton("🌬️ Nafas (2 daq)", callback_data="meditate_breathing"),
         InlineKeyboardButton("🧘 Tinchlanish (5 daq)", callback_data="meditate_calm")],
        [InlineKeyboardButton("😴 Uyqu (10 daq)", callback_data="meditate_sleep")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(get_text(lang, "meditate_ask"), reply_markup=reply_markup)

async def fitness_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_lang(update.effective_user.id)
    btns = get_workout_buttons(lang)
    keyboard = [
        [InlineKeyboardButton(btns["morning"], callback_data="workout_morning"),
         InlineKeyboardButton(btns["energy"], callback_data="workout_energy")],
        [InlineKeyboardButton(btns["relax"], callback_data="workout_relax")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(btns["ask"], reply_markup=reply_markup)

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
        text = f"🌿 **Assalomu alaykum, {name}!**\n\nMen sizning tabiiy shifokoringizman. Dardingizni ayting, tabiiy usullar bilan yordam beraman. ❤️"
    else:
        text = "🌿 **Tabiiy Shifokor**\n\nMen sizni tinglayman va tabiiy usullar bilan yordam beraman. Dardingizni, muammoingizni ayting. ❤️"
    
    await update.message.reply_text(text, parse_mode="Markdown")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    stats = get_user_stats(user_id)
    workout_count = get_workout_count(user_id)
    healer_count = get_healer_count(user_id)
    memories = get_user_memories(user_id)

    if stats["mood_count"] > 0:
        mood_emoji = ["😢", "😔", "😐", "🙂", "😄"][min(4, int(stats["avg_mood"]) - 1)]
    else:
        mood_emoji = "❓"

    # Xotiradan ma'lumotlar - Markdown escape bilan
    memory_info = ""
    for m in memories[:5]:
        if m["key"] != "last_mood":
            safe_key = escape_markdown(str(m['key']))
            safe_value = escape_markdown(str(m['value']))
            memory_info += f"• {safe_key}: {safe_value}\n"

    stats_text = f"""
📊 **Sizning statistikangiz**

😊 Kayfiyat yozuvlari: {stats["mood_count"]}
📝 Kundalik yozuvlari: {stats["journal_count"]}
💪 Mashqlar: {workout_count}
🌿 Shifokor seanslar: {healer_count}
{f"📈 O'rtacha kayfiyat: {mood_emoji} ({stats['avg_mood']:.1f}/5)" if stats["mood_count"] > 0 else ""}

🧠 **Men siz haqingizda bilganlarim:**
{memory_info if memory_info else "Hali ma'lumot to'planmagan"}

💡 Ko'proq suhbatlashsak, sizni yaxshiroq tushunaman!
    """
    await update.message.reply_text(stats_text, parse_mode="Markdown")

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    clear_conversations(user_id)
    context.user_data["mode"] = "normal"
    await update.message.reply_text("🔄 Suhbat tarixi tozalandi. Xotira saqlanadi.")

async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz"),
         InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🌍 Tilni tanlang:", reply_markup=reply_markup)

# === CALLBACK HANDLER ===

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lang = get_user_lang(user_id)

    # Til
    if query.data.startswith("lang_"):
        new_lang = query.data.split("_")[1]
        set_user_lang(user_id, new_lang)
        save_memory(user_id, "preferences", "language", new_lang, importance=2)
        await safe_edit(query, get_text(new_lang, "lang_changed"))
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
            text = f"💬 **{name}**, men sizni tinglayman! Qanday yordam bera olaman?"
        else:
            text = "💬 Men sizni tinglayman! Ismingiz nima, qanday yordam bera olaman?"
        await safe_edit(query, text, parse_mode="Markdown")
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
            text = f"🌿 **{name}**, yana ko'rishganimdan xursandman!\n\nOxirgi safar **{recent_problem}** haqida gaplashgan edik. Qanday bo'ldi? Yoki boshqa narsa bormi?"
        elif name:
            text = f"🌿 **{name}**, tabiiy shifokoringiz sizni tinglaydi. Qanday yordam kerak?"
        else:
            text = "🌿 **Tabiiy Shifokor** sizni tinglaydi.\n\nDardingizni ayting, tabiiy usullar bilan yordam beraman. ❤️"
        await safe_edit(query, text, parse_mode="Markdown")
        return

    # Mood
    if query.data.startswith("mood_") and query.data[5:].isdigit():
        score = int(query.data.split("_")[1])
        save_mood(user_id, score)
        emojis = {1: "😢", 2: "😔", 3: "😐", 4: "🙂", 5: "😄"}
        
        # Kayfiyatga mos javob
        if score <= 2:
            follow_up = "\n\n💬 Nima bo'ldi? Gaplashmoqchimisiz? Men sizni tinglayman..."
        elif score == 3:
            follow_up = "\n\n🤔 Normal kun. Biror narsa yaxshilash mumkinmi?"
        else:
            follow_up = "\n\n🌟 Ajoyib! Bugungi yaxshi kayfiyatingiz davom etsin!"
        
        response = f"{emojis[score]} Kayfiyatingiz saqlandi: {score}/5{follow_up}"
        await safe_edit(query, response)
        return

    # Journal
    if query.data == "journal":
        context.user_data["waiting_for"] = "journal"
        await safe_edit(query, get_text(lang, "journal_ask"), parse_mode="Markdown")
        return

    # Meditate
    if query.data == "meditate":
        keyboard = [
            [InlineKeyboardButton("🌬️ Nafas (2 daq)", callback_data="meditate_breathing"),
             InlineKeyboardButton("🧘 Tinchlanish (5 daq)", callback_data="meditate_calm")],
            [InlineKeyboardButton("😴 Uyqu (10 daq)", callback_data="meditate_sleep")]
        ]
        await safe_edit(query, get_text(lang, "meditate_ask"), reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if query.data == "meditate_breathing":
        text = """🌬️ **4-7-8 Nafas Mashqi**

1️⃣ Qulay o'tiring, ko'zingizni yuming
2️⃣ 4 soniya - nafas oling (burun orqali)
3️⃣ 7 soniya - nafasni ushlab turing
4️⃣ 8 soniya - sekin chiqaring (og'iz orqali)
5️⃣ 4-5 marta takrorlang

💡 Bu mashq asab tizimini tinchlantiradi va stressni kamaytiradi.

Mashq qildingizmi? Qanday his qilyapsiz? 😊"""
        await safe_edit(query, text, parse_mode="Markdown")
        return

    if query.data == "meditate_calm":
        text = """🧘 **5 Daqiqalik Tinchlanish**

1️⃣ Qulay joyga o'tiring
2️⃣ Ko'zingizni yuming
3️⃣ Chuqur nafas oling va chiqaring
4️⃣ Tanangizni bo'shating - boshdan oyoqqacha
5️⃣ Fikrlarga e'tibor bermang, ular o'tib ketsin
6️⃣ Faqat nafasingizga diqqat qiling

🕐 5 daqiqa shu holatda qoling

💭 Fikrlar kelsa - ularga yopishib qolmang, bulutlar kabi o'tkazib yuboring.

Yaxshi meditatsiya! 🙏"""
        await safe_edit(query, text, parse_mode="Markdown")
        return

    if query.data == "meditate_sleep":
        text = """😴 **Uyqu Meditatsiyasi**

🛏️ Yotib, ko'z yumganingizda:

1️⃣ 3 marta chuqur nafas oling
2️⃣ Oyoq barmoqlaridan boshlab bo'shating
3️⃣ Sekin yuqoriga ko'tariling - boldir, tizza, son...
4️⃣ Qorin, ko'krak, qo'llar...
5️⃣ Bo'yin, yuz, bosh...
6️⃣ Butun tana og'ir va bo'sh

🌙 O'zingizni bulut ustida his qiling...
⭐ Sekin-asta uyquga cho'ming...

Yoqimli tushlar ko'ring! 💫"""
        await safe_edit(query, text, parse_mode="Markdown")
        return

    # Fitness
    if query.data == "fitness":
        btns = get_workout_buttons(lang)
        keyboard = [
            [InlineKeyboardButton(btns["morning"], callback_data="workout_morning"),
             InlineKeyboardButton(btns["energy"], callback_data="workout_energy")],
            [InlineKeyboardButton(btns["relax"], callback_data="workout_relax")]
        ]
        await safe_edit(query, btns["ask"], reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if query.data.startswith("workout_done_"):
        workout_type = query.data.split("_")[2]
        save_workout(user_id, workout_type)
        await safe_edit(query, get_workout_done(lang) + "\n\n💪 Ajoyib! Davom eting!")
        return

    if query.data.startswith("workout_"):
        workout_type = query.data.split("_")[1]
        text = get_workout_text(lang, workout_type)
        keyboard = [[InlineKeyboardButton("✅ Bajardim!", callback_data=f"workout_done_{workout_type}")]]
        await safe_edit(query, text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    # Stats
    if query.data == "stats":
        stats = get_user_stats(user_id)
        workout_count = get_workout_count(user_id)
        healer_count = get_healer_count(user_id)
        
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
{f"📈 O'rtacha: {mood_emoji} ({stats['avg_mood']:.1f}/5)" if stats["mood_count"] > 0 else ""}
        """
        await safe_edit(query, stats_text, parse_mode="Markdown")
        return

    if query.data == "lang":
        keyboard = [
            [InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz"),
             InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
            [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
        ]
        await safe_edit(query, "🌍 Tilni tanlang:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

# === MESSAGE HANDLER ===

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text
    lang = get_user_lang(user_id)
    
    # Journal
    if context.user_data.get("waiting_for") == "journal":
        save_journal(user_id, user_message)
        context.user_data["waiting_for"] = None
        await update.message.reply_text(get_text(lang, "journal_saved") + "\n\n💭 Yozganlaringiz sizning shaxsiy fikrlaringiz. Men ularni eslab qolaman.")
        return
    
    # Typing animation
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # AI Response
    mode = context.user_data.get("mode", "normal")
    response = await get_ai_response(user_id, user_message, mode)
    await update.message.reply_text(response)

# === MAIN ===

def main():
    if not TELEGRAM_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN topilmadi!")
        logger.error("📝 .env faylni yarating va TELEGRAM_BOT_TOKEN qo'shing")
        logger.error("💡 .env.example faylini ko'rib chiqing")
        return
    if not OPENAI_API_KEY:
        logger.warning("⚠️ OPENAI_API_KEY topilmadi! AI funksiyalar ishlamaydi.")
        logger.warning("📝 .env fayliga OPENAI_API_KEY qo'shishni unutmang")

    if DATABASE_URL:
        init_db()
    else:
        logger.warning("⚠️ DATABASE_URL topilmadi! Ma'lumotlar saqlanmaydi.")

    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("mood", mood_command))
    app.add_handler(CommandHandler("journal", journal_command))
    app.add_handler(CommandHandler("meditate", meditate_command))
    app.add_handler(CommandHandler("fitness", fitness_command))
    app.add_handler(CommandHandler("healer", healer_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("reset", reset_command))
    app.add_handler(CommandHandler("lang", lang_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("✅ MindMate JARVIS bot ishga tushdi!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()