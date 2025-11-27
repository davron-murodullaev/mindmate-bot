import os
import logging
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from openai import OpenAI
from languages import get_text, get_mood_response, TRANSLATIONS

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

client = OpenAI(api_key=OPENAI_API_KEY)

# === DATABASE ===

def get_db():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            language TEXT DEFAULT 'uz',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS moods (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            score INTEGER,
            note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS journals (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            role TEXT,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()
    logger.info("✅ Database initialized")

def save_user(user_id, username, lang="uz"):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO users (user_id, username, language) VALUES (%s, %s, %s)
        ON CONFLICT (user_id) DO UPDATE SET username = %s
    ''', (user_id, username, lang, username))
    conn.commit()
    cur.close()
    conn.close()

def get_user_lang(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT language FROM users WHERE user_id = %s', (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] if row else "uz"

def set_user_lang(user_id, lang):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('UPDATE users SET language = %s WHERE user_id = %s', (lang, user_id))
    conn.commit()
    cur.close()
    conn.close()

def save_mood(user_id, score, note=None):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO moods (user_id, score, note) VALUES (%s, %s, %s)', (user_id, score, note))
    conn.commit()
    cur.close()
    conn.close()

def save_journal(user_id, text):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO journals (user_id, text) VALUES (%s, %s)', (user_id, text))
    conn.commit()
    cur.close()
    conn.close()

def get_user_stats(user_id):
    conn = get_db()
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

def save_conversation(user_id, role, content):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO conversations (user_id, role, content) VALUES (%s, %s, %s)', (user_id, role, content))
    conn.commit()
    cur.close()
    conn.close()

def get_conversations(user_id, limit=20):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        SELECT role, content FROM conversations 
        WHERE user_id = %s ORDER BY created_at DESC LIMIT %s
    ''', (user_id, limit))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"role": r[0], "content": r[1]} for r in reversed(rows)]

def clear_conversations(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM conversations WHERE user_id = %s', (user_id,))
    conn.commit()
    cur.close()
    conn.close()

# === AI ===

def get_system_prompt(lang):
    prompts = {
        "uz": """Sen MindMate - mehribon AI psixolog. O'zbek tilida gapir. Qisqa va samimiy javob ber (3-5 gap).""",
        "ru": """Ты MindMate - добрый AI психолог. Говори на русском. Отвечай кратко и душевно (3-5 предложений).""",
        "en": """You are MindMate - a kind AI psychologist. Speak English. Give short, warm responses (3-5 sentences)."""
    }
    return prompts.get(lang, prompts["en"])

async def get_ai_response(user_id: int, message: str) -> str:
    lang = get_user_lang(user_id)
    conversations = get_conversations(user_id)
    
    messages = [{"role": "system", "content": get_system_prompt(lang)}]
    messages.extend(conversations)
    messages.append({"role": "user", "content": message})
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        ai_message = response.choices[0].message.content
        
        save_conversation(user_id, "user", message)
        save_conversation(user_id, "assistant", ai_message)
        
        return ai_message
    except Exception as e:
        logger.error(f"OpenAI xatosi: {e}")
        return get_text(lang, "error")

# === BUYRUQLAR ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user.id, user.username)
    lang = get_user_lang(user.id)
    
    keyboard = [
        [InlineKeyboardButton(get_text(lang, "btn_mood"), callback_data="mood"),
         InlineKeyboardButton(get_text(lang, "btn_journal"), callback_data="journal")],
        [InlineKeyboardButton(get_text(lang, "btn_meditate"), callback_data="meditate"),
         InlineKeyboardButton(get_text(lang, "btn_stats"), callback_data="stats")],
        [InlineKeyboardButton(get_text(lang, "btn_chat"), callback_data="chat"),
         InlineKeyboardButton(get_text(lang, "btn_help"), callback_data="help")],
        [InlineKeyboardButton("🌍 Language", callback_data="lang")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(get_text(lang, "welcome"), reply_markup=reply_markup, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_lang(update.effective_user.id)
    await update.message.reply_text(get_text(lang, "help"), parse_mode="Markdown")

async def mood_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_lang(update.effective_user.id)
    keyboard = [
        [InlineKeyboardButton(get_text(lang, "mood_5"), callback_data="mood_5"),
         InlineKeyboardButton(get_text(lang, "mood_4"), callback_data="mood_4")],
        [InlineKeyboardButton(get_text(lang, "mood_3"), callback_data="mood_3"),
         InlineKeyboardButton(get_text(lang, "mood_2"), callback_data="mood_2")],
        [InlineKeyboardButton(get_text(lang, "mood_1"), callback_data="mood_1")]
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
        [InlineKeyboardButton(get_text(lang, "meditate_breathing"), callback_data="meditate_breathing"),
         InlineKeyboardButton(get_text(lang, "meditate_calm"), callback_data="meditate_calm")],
        [InlineKeyboardButton(get_text(lang, "meditate_sleep"), callback_data="meditate_sleep")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(get_text(lang, "meditate_ask"), reply_markup=reply_markup)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    stats = get_user_stats(user_id)
    
    if stats["mood_count"] > 0:
        mood_emoji = ["😢", "😔", "😐", "🙂", "😄"][min(4, int(stats["avg_mood"]) - 1)]
    else:
        mood_emoji = "❓"
    
    stats_text = f"""
{get_text(lang, "stats_title")}

{get_text(lang, "stats_moods")}: {stats["mood_count"]}
{get_text(lang, "stats_journals")}: {stats["journal_count"]}
{f"{get_text(lang, 'stats_avg')}: {mood_emoji} ({stats['avg_mood']:.1f}/5)" if stats["mood_count"] > 0 else ""}

{get_text(lang, "stats_tip")}
    """
    await update.message.reply_text(stats_text, parse_mode="Markdown")

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    clear_conversations(user_id)
    await update.message.reply_text(get_text(lang, "reset_done"))

async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz"),
         InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🌍 Tilni tanlang / Choose language:", reply_markup=reply_markup)

# === CALLBACK HANDLER ===

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lang = get_user_lang(user_id)
    
    # Til o'zgartirish
    if query.data.startswith("lang_"):
        new_lang = query.data.split("_")[1]
        set_user_lang(user_id, new_lang)
        await query.edit_message_text(get_text(new_lang, "lang_changed"))
        return
    
    # Kayfiyat saqlash
    if query.data.startswith("mood_") and query.data[5:].isdigit():
        score = int(query.data.split("_")[1])
        save_mood(user_id, score)
        emojis = {1: "😢", 2: "😔", 3: "😐", 4: "🙂", 5: "😄"}
        response = get_mood_response(lang, score)
        await query.edit_message_text(f"{emojis[score]} {get_text(lang, 'mood_saved')}\n\n{response}")
        return
    
    if query.data == "mood":
        keyboard = [
            [InlineKeyboardButton(get_text(lang, "mood_5"), callback_data="mood_5"),
             InlineKeyboardButton(get_text(lang, "mood_4"), callback_data="mood_4")],
            [InlineKeyboardButton(get_text(lang, "mood_3"), callback_data="mood_3"),
             InlineKeyboardButton(get_text(lang, "mood_2"), callback_data="mood_2")],
            [InlineKeyboardButton(get_text(lang, "mood_1"), callback_data="mood_1")]
        ]
        await query.edit_message_text(get_text(lang, "mood_ask"), reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif query.data == "journal":
        context.user_data["waiting_for"] = "journal"
        await query.edit_message_text(get_text(lang, "journal_ask"), parse_mode="Markdown")
    
    elif query.data == "meditate":
        keyboard = [
            [InlineKeyboardButton(get_text(lang, "meditate_breathing"), callback_data="meditate_breathing"),
             InlineKeyboardButton(get_text(lang, "meditate_calm"), callback_data="meditate_calm")],
            [InlineKeyboardButton(get_text(lang, "meditate_sleep"), callback_data="meditate_sleep")]
        ]
        await query.edit_message_text(get_text(lang, "meditate_ask"), reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif query.data == "meditate_breathing":
        texts = {
            "uz": "🌬️ **Nafas olish (2 daq)**\n\n1. 4 soniya nafas oling\n2. 4 soniya ushlab turing\n3. 4 soniya chiqaring\n4. 5 marta takrorlang",
            "ru": "🌬️ **Дыхание (2 мин)**\n\n1. 4 сек вдох\n2. 4 сек задержка\n3. 4 сек выдох\n4. Повторите 5 раз",
            "en": "🌬️ **Breathing (2 min)**\n\n1. 4 sec inhale\n2. 4 sec hold\n3. 4 sec exhale\n4. Repeat 5 times"
        }
        await query.edit_message_text(texts.get(lang, texts["en"]), parse_mode="Markdown")
    
    elif query.data == "meditate_calm":
        texts = {
            "uz": "🧘 **Tinchlanish (5 daq)**\n\n1. Qulay o'tiring\n2. Ko'zni yuming\n3. Nafasga e'tibor bering\n4. Fikrlarni qo'yib yuboring",
            "ru": "🧘 **Спокойствие (5 мин)**\n\n1. Сядьте удобно\n2. Закройте глаза\n3. Следите за дыханием\n4. Отпустите мысли",
            "en": "🧘 **Calm (5 min)**\n\n1. Sit comfortably\n2. Close your eyes\n3. Focus on breath\n4. Let thoughts go"
        }
        await query.edit_message_text(texts.get(lang, texts["en"]), parse_mode="Markdown")
    
    elif query.data == "meditate_sleep":
        texts = {
            "uz": "😴 **Uyqu (10 daq)**\n\n1. Yoting va ko'z yuming\n2. Tanani bo'shating\n3. Sekin nafas oling\n4. Uyquga cho'ming\n\n🌙 Yoqimli tushlar!",
            "ru": "😴 **Сон (10 мин)**\n\n1. Лягте и закройте глаза\n2. Расслабьте тело\n3. Дышите медленно\n4. Погрузитесь в сон\n\n🌙 Сладких снов!",
            "en": "😴 **Sleep (10 min)**\n\n1. Lie down, close eyes\n2. Relax your body\n3. Breathe slowly\n4. Drift to sleep\n\n🌙 Sweet dreams!"
        }
        await query.edit_message_text(texts.get(lang, texts["en"]), parse_mode="Markdown")
    
    elif query.data == "stats":
        stats = get_user_stats(user_id)
        if stats["mood_count"] > 0:
            mood_emoji = ["😢", "😔", "😐", "🙂", "😄"][min(4, int(stats["avg_mood"]) - 1)]
        else:
            mood_emoji = "❓"
        stats_text = f"""
{get_text(lang, "stats_title")}

{get_text(lang, "stats_moods")}: {stats["mood_count"]}
{get_text(lang, "stats_journals")}: {stats["journal_count"]}
{f"{get_text(lang, 'stats_avg')}: {mood_emoji} ({stats['avg_mood']:.1f}/5)" if stats["mood_count"] > 0 else ""}
        """
        await query.edit_message_text(stats_text, parse_mode="Markdown")
    
    elif query.data == "chat":
        await query.edit_message_text(get_text(lang, "chat_start"))
    
    elif query.data == "help":
        await query.edit_message_text(get_text(lang, "help"), parse_mode="Markdown")
    
    elif query.data == "lang":
        keyboard = [
            [InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz"),
             InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
            [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
        ]
        await query.edit_message_text(get_text(lang, "lang_ask"), reply_markup=InlineKeyboardMarkup(keyboard))

# === XABAR HANDLER ===

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text
    lang = get_user_lang(user_id)
    
    if context.user_data.get("waiting_for") == "journal":
        save_journal(user_id, user_message)
        context.user_data["waiting_for"] = None
        await update.message.reply_text(get_text(lang, "journal_saved"))
        return
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    response = await get_ai_response(user_id, user_message)
    await update.message.reply_text(response)

# === MAIN ===

def main():
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN topilmadi!")
        return
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY topilmadi!")
        return
    
    if DATABASE_URL:
        init_db()
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("mood", mood_command))
    app.add_handler(CommandHandler("journal", journal_command))
    app.add_handler(CommandHandler("meditate", meditate_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("reset", reset_command))
    app.add_handler(CommandHandler("lang", lang_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("✅ MindMate bot ishga tushdi!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()