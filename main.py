import os
import logging
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from openai import OpenAI

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

def save_user(user_id, username):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO users (user_id, username) VALUES (%s, %s)
        ON CONFLICT (user_id) DO UPDATE SET username = %s
    ''', (user_id, username, username))
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

SYSTEM_PROMPT = """Sen MindMate - mehribon va tushunuvchi AI psixolog va hayot yordamchisisan.

Vazifang:
- Odamlarga ruhiy yordam berish
- Stressni yengillashtirishga yordam
- Motivatsiya va qo'llab-quvvatlash
- Sog'lom odatlar shakllantirishga yordam

Qoidalar:
- Foydalanuvchi tilida gapir (o'zbek, rus, ingliz va boshqalar)
- Mehribon va samimiy bo'l
- Hukm qilma, faqat qo'llab-quvvatla
- Javoblar qisqa va aniq bo'lsin (3-5 gap)
- Kerak bo'lsa, professional yordamga yo'naltir
"""

async def get_ai_response(user_id: int, message: str) -> str:
    conversations = get_conversations(user_id)
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
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
        return "Kechirasiz, hozir javob bera olmayapman. Keyinroq urinib ko'ring."

# === BUYRUQLAR ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user.id, user.username)
    
    keyboard = [
        [InlineKeyboardButton("😊 Kayfiyat", callback_data="mood"),
         InlineKeyboardButton("📝 Kundalik", callback_data="journal")],
        [InlineKeyboardButton("🧘 Meditatsiya", callback_data="meditate"),
         InlineKeyboardButton("📊 Statistika", callback_data="stats")],
        [InlineKeyboardButton("💬 Suhbat", callback_data="chat"),
         InlineKeyboardButton("❓ Yordam", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome = """
🌟 **Salom! Men MindMate** - sizning shaxsiy AI yordamchingizman.

Men sizga yordam bera olaman:
- 😊 Kayfiyatingizni kuzatish
- 📝 Kundalik yozish
- 🧘 Meditatsiya qilish
- 💬 Suhbatlashish va maslahat olish

Quyidagi tugmalardan birini tanlang yoki shunchaki xabar yozing!
    """
    await update.message.reply_text(welcome, reply_markup=reply_markup, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📚 **MindMate Yordam**

**Buyruqlar:**
/start - Bosh menyu
/mood - Kayfiyatni belgilash
/journal - Kundalik yozish
/meditate - Meditatsiya
/stats - Statistika
/reset - Suhbatni yangilash

💡 Yoki shunchaki xabar yozing - men sizni tinglayman!
    """
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def mood_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("😄 Ajoyib", callback_data="mood_5"),
         InlineKeyboardButton("🙂 Yaxshi", callback_data="mood_4")],
        [InlineKeyboardButton("😐 Normal", callback_data="mood_3"),
         InlineKeyboardButton("😔 Yomon", callback_data="mood_2")],
        [InlineKeyboardButton("😢 Juda yomon", callback_data="mood_1")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Bugun o'zingizni qanday his qilyapsiz?", reply_markup=reply_markup)

async def journal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["waiting_for"] = "journal"
    await update.message.reply_text(
        "📝 **Kundalik**\n\nBugun nima bo'ldi? His-tuyg'ularingizni yozing...",
        parse_mode="Markdown"
    )

async def meditate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌬️ Nafas olish (2 daq)", callback_data="meditate_breathing"),
         InlineKeyboardButton("🧘 Tinchlanish (5 daq)", callback_data="meditate_calm")],
        [InlineKeyboardButton("😴 Uyqu uchun (10 daq)", callback_data="meditate_sleep")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🧘 Qaysi meditatsiyani tanlaysiz?", reply_markup=reply_markup)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    stats = get_user_stats(user_id)
    
    if stats["mood_count"] > 0:
        mood_emoji = ["😢", "😔", "😐", "🙂", "😄"][min(4, int(stats["avg_mood"]) - 1)]
    else:
        mood_emoji = "❓"
    
    stats_text = f"""
📊 **Sizning statistikangiz**

😊 Kayfiyat yozuvlari: {stats["mood_count"]}
📝 Kundalik yozuvlari: {stats["journal_count"]}
{f"📈 O'rtacha kayfiyat: {mood_emoji} ({stats['avg_mood']:.1f}/5)" if stats["mood_count"] > 0 else ""}

💡 Har kuni kayfiyatingizni belgilang va kundalik yozing!
    """
    await update.message.reply_text(stats_text, parse_mode="Markdown")

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    clear_conversations(user_id)
    await update.message.reply_text("🔄 Suhbat yangilandi!")

# === CALLBACK HANDLER ===

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if query.data.startswith("mood_"):
        score = int(query.data.split("_")[1])
        save_mood(user_id, score)
        emojis = {1: "😢", 2: "😔", 3: "😐", 4: "🙂", 5: "😄"}
        
        responses = {
            1: "Tushunaman, og'ir kun bo'lyapti. Men shu yerdaman. Nima qiynayapti?",
            2: "Har kimda bunday kunlar bo'ladi. Gaplashmoqchimisiz?",
            3: "Tushundim. Kayfiyatingizni yaxshilash uchun biror narsa qilaylikmi?",
            4: "Yaxshi! Bugun nima yaxshi bo'ldi?",
            5: "Ajoyib! Sizning baxtingiz meni ham xursand qiladi! 🌟"
        }
        await query.edit_message_text(f"{emojis[score]} Kayfiyat saqlandi!\n\n{responses[score]}")
    
    elif query.data == "mood":
        keyboard = [
            [InlineKeyboardButton("😄 Ajoyib", callback_data="mood_5"),
             InlineKeyboardButton("🙂 Yaxshi", callback_data="mood_4")],
            [InlineKeyboardButton("😐 Normal", callback_data="mood_3"),
             InlineKeyboardButton("😔 Yomon", callback_data="mood_2")],
            [InlineKeyboardButton("😢 Juda yomon", callback_data="mood_1")]
        ]
        await query.edit_message_text("Bugun o'zingizni qanday his qilyapsiz?", 
                                       reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif query.data == "journal":
        context.user_data["waiting_for"] = "journal"
        await query.edit_message_text("📝 **Kundalik**\n\nBugun nima bo'ldi? His-tuyg'ularingizni yozing...",
                                       parse_mode="Markdown")
    
    elif query.data == "meditate":
        keyboard = [
            [InlineKeyboardButton("🌬️ Nafas (2 daq)", callback_data="meditate_breathing"),
             InlineKeyboardButton("🧘 Tinchlanish (5 daq)", callback_data="meditate_calm")],
            [InlineKeyboardButton("😴 Uyqu (10 daq)", callback_data="meditate_sleep")]
        ]
        await query.edit_message_text("🧘 Qaysi meditatsiyani tanlaysiz?",
                                       reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif query.data == "meditate_breathing":
        text = """
🌬️ **Nafas olish mashqi (2 daqiqa)**

1. Qulay holat oling
2. Ko'zingizni yuming
3. 4 soniya - chuqur nafas oling
4. 4 soniya - nafasni ushlab turing
5. 4 soniya - sekin chiqaring
6. 5 marta takrorlang

🔄 Tayyor bo'lgach, yana /meditate bosing
        """
        await query.edit_message_text(text, parse_mode="Markdown")
    
    elif query.data == "meditate_calm":
        text = """
🧘 **Tinchlanish mashqi (5 daqiqa)**

1. Tinch joyda o'tiring
2. Ko'zingizni yuming
3. Tanangizning har bir qismini bo'shating
4. Faqat nafasingizga e'tibor bering
5. Fikrlar kelsa - kuzating va qo'yib yuboring
6. 5 daqiqa davom eting

🕯️ Ichki tinchlikni his qiling...
        """
        await query.edit_message_text(text, parse_mode="Markdown")
    
    elif query.data == "meditate_sleep":
        text = """
😴 **Uyqu meditatsiyasi (10 daqiqa)**

1. Yotgan holda ko'zingizni yuming
2. Oyoq barmoqlaridan boshlab tanani bo'shating
3. Har bir nafasda tanangiz og'irlashsin
4. O'zingizni bulut ustida tasavvur qiling
5. Barcha tashvishlarni qo'yib yuboring
6. Sekin-asta uyquga cho'ming...

🌙 Yoqimli tushlar!
        """
        await query.edit_message_text(text, parse_mode="Markdown")
    
    elif query.data == "stats":
        stats = get_user_stats(user_id)
        if stats["mood_count"] > 0:
            mood_emoji = ["😢", "😔", "😐", "🙂", "😄"][min(4, int(stats["avg_mood"]) - 1)]
        else:
            mood_emoji = "❓"
        
        stats_text = f"""
📊 **Sizning statistikangiz**

😊 Kayfiyat yozuvlari: {stats["mood_count"]}
📝 Kundalik yozuvlari: {stats["journal_count"]}
{f"📈 O'rtacha kayfiyat: {mood_emoji} ({stats['avg_mood']:.1f}/5)" if stats["mood_count"] > 0 else ""}
        """
        await query.edit_message_text(stats_text, parse_mode="Markdown")
    
    elif query.data == "chat":
        await query.edit_message_text("💬 Yaxshi! Menga xabar yozing, men sizni tinglayman...")
    
    elif query.data == "help":
        help_text = """
📚 **MindMate Yordam**

/start - Bosh menyu
/mood - Kayfiyat belgilash
/journal - Kundalik yozish
/meditate - Meditatsiya
/stats - Statistika

💬 Yoki shunchaki yozing!
        """
        await query.edit_message_text(help_text, parse_mode="Markdown")

# === XABAR HANDLER ===

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text
    
    if context.user_data.get("waiting_for") == "journal":
        save_journal(user_id, user_message)
        context.user_data["waiting_for"] = None
        await update.message.reply_text(
            "✅ Kundalik saqlandi!\n\n💬 Fikrlaringiz haqida gaplashmoqchimisiz?"
        )
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
    
    # Database ni ishga tushirish
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
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("✅ MindMate bot ishga tushdi!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()