import os
import logging
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from openai import OpenAI
from languages import get_text, get_mood_response, TRANSLATIONS
from fitness import get_workout_text, get_workout_buttons, get_workout_done, get_workout_stats_label

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
        logger.error(f"❌ DB ulanish xatosi: {e}")
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
    cur.execute('''
        CREATE TABLE IF NOT EXISTS workouts (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            workout_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()
    logger.info("✅ Database initialized")

def save_user(user_id, username, lang="uz"):
    conn = get_db()
    if conn is None:
        logger.error("DB yo'q (save_user)")
        return
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
    if conn is None:
        logger.error("DB yo'q (get_user_lang)")
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
        logger.error("DB yo'q (set_user_lang)")
        return
    cur = conn.cursor()
    cur.execute('UPDATE users SET language = %s WHERE user_id = %s', (lang, user_id))
    conn.commit()
    cur.close()
    conn.close()

def save_mood(user_id, score, note=None):
    conn = get_db()
    if conn is None:
        logger.error("DB yo'q (save_mood)")
        return
    cur = conn.cursor()
    cur.execute('INSERT INTO moods (user_id, score, note) VALUES (%s, %s, %s)', (user_id, score, note))
    conn.commit()
    cur.close()
    conn.close()

def save_journal(user_id, text):
    conn = get_db()
    if conn is None:
        logger.error("DB yo'q (save_journal)")
        return
    cur = conn.cursor()
    cur.execute('INSERT INTO journals (user_id, text) VALUES (%s, %s)', (user_id, text))
    conn.commit()
    cur.close()
    conn.close()

def get_user_stats(user_id):
    conn = get_db()
    if conn is None:
        logger.error("DB yo'q (get_user_stats)")
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

def save_workout(user_id, workout_type):
    conn = get_db()
    if conn is None:
        logger.error("DB yo'q (save_workout)")
        return
    cur = conn.cursor()
    cur.execute('INSERT INTO workouts (user_id, workout_type) VALUES (%s, %s)', (user_id, workout_type))
    conn.commit()
    cur.close()
    conn.close()

def get_workout_count(user_id):
    conn = get_db()
    if conn is None:
        logger.error("DB yo'q (get_workout_count)")
        return 0
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM workouts WHERE user_id = %s', (user_id,))
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count or 0

def save_conversation(user_id, role, content):
    conn = get_db()
    if conn is None:
        logger.error("DB yo'q (save_conversation)")
        return
    cur = conn.cursor()
    cur.execute('INSERT INTO conversations (user_id, role, content) VALUES (%s, %s, %s)', (user_id, role, content))
    conn.commit()
    cur.close()
    conn.close()

def get_conversations(user_id, limit=20):
    conn = get_db()
    if conn is None:
        logger.error("DB yo'q (get_conversations)")
        return []
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
    if conn is None:
        logger.error("DB yo'q (clear_conversations)")
        return
    cur = conn.cursor()
    cur.execute('DELETE FROM conversations WHERE user_id = %s', (user_id,))
    conn.commit()
    cur.close()
    conn.close()

# === SAFE EDIT ===
async def safe_edit(query, text, reply_markup=None, parse_mode=None):
    try:
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )
    except Exception as e:
        logger.error(f"edit_message_text xato: {e}")
        try:
            await query.message.reply_text(
                text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
        except Exception as e2:
            logger.error(f"fallback reply xato: {e2}")

# === UI HELPERS (PREMIUM STYLE) ===

def get_home_text(lang: str) -> str:
    texts = {
        "uz": (
            "🌟 *MindMate – sizning shaxsiy AI hamrohingiz*\n\n"
            "Men sizga quyidagilarda yordam bera olaman:\n"
            "• 🙂 Kayfiyatni kuzatish va tahlil qilish\n"
            "• 📝 Kundalik orqali o'zingizni yozib borish\n"
            "• 🧘 Meditatsiya va tinchlanish mashqlari\n"
            "• 💪 Eng oddiy uy sharoitidagi mashqlar\n"
            "• 💬 Iliq suhbat va ruhiy ko‘mak\n\n"
            "Quyidagi menyudan tanlang yoki shunchaki yozishni boshlang."
        ),
        "ru": (
            "🌟 *MindMate – твой личный AI-помощник*\n\n"
            "Я могу помочь тебе с:\n"
            "• 🙂 Отслеживанием настроения\n"
            "• 📝 Ведением личного дневника\n"
            "• 🧘 Медитациями и расслаблением\n"
            "• 💪 Лёгкими домашними тренировками\n"
            "• 💬 Тёплой поддерживающей беседой\n\n"
            "Выбери пункт в меню или просто напиши сообщение."
        ),
        "en": (
            "🌟 *MindMate – your personal AI companion*\n\n"
            "I can help you with:\n"
            "• 🙂 Tracking and reflecting on your mood\n"
            "• 📝 Writing a gentle daily journal\n"
            "• 🧘 Short calming meditations\n"
            "• 💪 Simple at-home workouts\n"
            "• 💬 Supportive, human-like conversations\n\n"
            "Pick an option from the menu or just start typing."
        )
    }
    return texts.get(lang, texts["en"])

def get_main_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    # callback_data lar eski logika bilan bir xil
    keyboard = [
        [
            InlineKeyboardButton("🙂 Kayfiyat", callback_data="mood"),
            InlineKeyboardButton("📝 Kundalik", callback_data="journal"),
        ],
        [
            InlineKeyboardButton("🧘 Meditatsiya", callback_data="meditate"),
            InlineKeyboardButton("💪 Fitness", callback_data="fitness"),
        ],
        [
            InlineKeyboardButton("📊 Statistika", callback_data="stats"),
            InlineKeyboardButton("💬 AI bilan suhbat", callback_data="chat"),
        ],
        [
            InlineKeyboardButton("🌍 Language", callback_data="lang"),
            InlineKeyboardButton("❓ Yordam", callback_data="help"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_mood_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("😄 Juda yaxshi (5)", callback_data="mood_5")],
        [InlineKeyboardButton("🙂 Yaxshi (4)", callback_data="mood_4")],
        [InlineKeyboardButton("😐 O‘rtacha (3)", callback_data="mood_3")],
        [InlineKeyboardButton("😔 Yomon (2)", callback_data="mood_2")],
        [InlineKeyboardButton("😢 Juda yomon (1)", callback_data="mood_1")],
        [InlineKeyboardButton("🏠 Bosh menyu", callback_data="home")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_meditate_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(get_text(lang, "meditate_breathing"), callback_data="meditate_breathing")
        ],
        [
            InlineKeyboardButton(get_text(lang, "meditate_calm"), callback_data="meditate_calm")
        ],
        [
            InlineKeyboardButton(get_text(lang, "meditate_sleep"), callback_data="meditate_sleep")
        ],
        [
            InlineKeyboardButton("🏠 Bosh menyu", callback_data="home")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_home_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Bosh menyu", callback_data="home")]])

# === AI ===

def get_system_prompt(lang):
    prompts = {
        "uz": (
            "Sen MindMate – mehribon, sokin ohangda gapiradigan AI psixologsan. "
            "O'zbek tilida yoz. 3–5 gap atrofida qisqa, ammo samimiy, tushunarli va "
            "tinchlantiruvchi javoblar ber. Nasihat berayotganda muloyim bo‘l."
        ),
        "ru": (
            "Ты MindMate – добрый, спокойный AI-психолог. Говори на русском. "
            "Отвечай коротко (3–5 предложений), тепло и поддерживающе. "
            "Избегай сухой, формальной речи."
        ),
        "en": (
            "You are MindMate – a calm, kind AI psychologist. Speak in warm, natural English. "
            "Answer in 3–5 sentences, with supportive and practical advice. "
            "Avoid sounding like a robot or a lecturer."
        ),
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

    text = get_home_text(lang)
    keyboard = get_main_menu_keyboard(lang)
    await update.message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_lang(update.effective_user.id)
    # mavjud help matnini premium ko‘rinishda chiqaramiz
    base_help = get_text(lang, "help")
    text = f"❓ *Yordam*\n\n{base_help}\n\n" \
           "💡 *Maslahat:* agar nima yozishni bilmasangiz, shunchaki kayfiyatingizni yoki bugungi kuningizni tasvirlab bering."
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_back_home_keyboard())

async def mood_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_lang(update.effective_user.id)
    text = get_text(lang, "mood_ask")
    await update.message.reply_text(text, reply_markup=get_mood_keyboard())

async def journal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_lang(update.effective_user.id)
    context.user_data["waiting_for"] = "journal"
    text = get_text(lang, "journal_ask")
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_back_home_keyboard())

async def meditate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_lang(update.effective_user.id)
    text = get_text(lang, "meditate_ask")
    await update.message.reply_text(text, reply_markup=get_meditate_menu_keyboard(lang))

async def fitness_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_lang(update.effective_user.id)
    btns = get_workout_buttons(lang)
    keyboard = [
        [
            InlineKeyboardButton(btns["morning"], callback_data="workout_morning")
        ],
        [
            InlineKeyboardButton(btns["energy"], callback_data="workout_energy")
        ],
        [
            InlineKeyboardButton(btns["relax"], callback_data="workout_relax")
        ],
        [
            InlineKeyboardButton("🏠 Bosh menyu", callback_data="home")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(btns["ask"], reply_markup=reply_markup)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    stats = get_user_stats(user_id)
    workout_count = get_workout_count(user_id)
    
    if stats["mood_count"] > 0:
        mood_emoji = ["😢", "😔", "😐", "🙂", "😄"][min(4, int(stats["avg_mood"]) - 1)]
        avg_line = f"{get_text(lang, 'stats_avg')}: {mood_emoji} ({stats['avg_mood']:.1f}/5)"
    else:
        mood_emoji = "❓"
        avg_line = ""

    text = (
        f"📊 *{get_text(lang, 'stats_title')}*\n\n"
        f"{get_text(lang, 'stats_moods')}: *{stats['mood_count']}*\n"
        f"{get_text(lang, 'stats_journals')}: *{stats['journal_count']}*\n"
        f"{get_workout_stats_label(lang)}: *{workout_count}*\n"
    )
    if avg_line:
        text += f"{avg_line}\n"

    text += f"\n{get_text(lang, 'stats_tip')}"
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_back_home_keyboard())

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    clear_conversations(user_id)
    await update.message.reply_text(get_text(lang, "reset_done"), reply_markup=get_back_home_keyboard())

async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz")
        ],
        [
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")
        ],
        [
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")
        ],
        [
            InlineKeyboardButton("🏠 Bosh menyu", callback_data="home")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🌍 Tilni tanlang / Choose language:", reply_markup=reply_markup)

# === CALLBACK HANDLER ===

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lang = get_user_lang(user_id)

    # Bosh menyuga qaytish
    if query.data == "home":
        await safe_edit(query, get_home_text(lang), reply_markup=get_main_menu_keyboard(lang), parse_mode="Markdown")
        return

    # Til o'zgartirish
    if query.data.startswith("lang_"):
        new_lang = query.data.split("_")[1]
        set_user_lang(user_id, new_lang)
        await safe_edit(query, get_text(new_lang, "lang_changed"), reply_markup=get_main_menu_keyboard(new_lang))
        return
    
    # Kayfiyat saqlash
    if query.data.startswith("mood_") and query.data[5:].isdigit():
        score = int(query.data.split("_")[1])
        save_mood(user_id, score)
        emojis = {1: "😢", 2: "😔", 3: "😐", 4: "🙂", 5: "😄"}
        response = get_mood_response(lang, score)
        text = f"{emojis[score]} {get_text(lang, 'mood_saved')}\n\n{response}"
        await safe_edit(query, text, reply_markup=get_back_home_keyboard())
        return

    # Workout done
    if query.data.startswith("workout_done_"):
        workout_type = query.data.split("_")[2]
        save_workout(user_id, workout_type)
        await safe_edit(query, get_workout_done(lang), reply_markup=get_back_home_keyboard())
        return

    # Workout start
    if query.data.startswith("workout_") and not query.data.startswith("workout_done_"):
        workout_type = query.data.split("_")[1]
        text = get_workout_text(lang, workout_type)
        keyboard = [
            [
                InlineKeyboardButton("✅ Tayyor / Done", callback_data=f"workout_done_{workout_type}")
            ],
            [
                InlineKeyboardButton("🏠 Bosh menyu", callback_data="home")
            ]
        ]
        await safe_edit(query, text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return
    
    if query.data == "fitness":
        btns = get_workout_buttons(lang)
        keyboard = [
            [
                InlineKeyboardButton(btns["morning"], callback_data="workout_morning")
            ],
            [
                InlineKeyboardButton(btns["energy"], callback_data="workout_energy")
            ],
            [
                InlineKeyboardButton(btns["relax"], callback_data="workout_relax")
            ],
            [
                InlineKeyboardButton("🏠 Bosh menyu", callback_data="home")
            ]
        ]
        await safe_edit(query, btns["ask"], reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if query.data == "mood":
        await safe_edit(query, get_text(lang, "mood_ask"), reply_markup=get_mood_keyboard())
        return

    if query.data == "journal":
        context.user_data["waiting_for"] = "journal"
        await safe_edit(query, get_text(lang, "journal_ask"), reply_markup=get_back_home_keyboard(), parse_mode="Markdown")
        return

    if query.data == "meditate":
        await safe_edit(query, get_text(lang, "meditate_ask"), reply_markup=get_meditate_menu_keyboard(lang))
        return

    if query.data == "meditate_breathing":
        texts = {
            "uz": "🌬️ **Nafas olish (2 daq)**\n\n1. 4 soniya nafas oling\n2. 4 soniya ushlab turing\n3. 4 soniya chiqaring\n4. Buni 5 marta takrorlang.\n\nSekin va ongli nafas oling.",
            "ru": "🌬️ **Дыхание (2 мин)**\n\n1. 4 секунды вдох\n2. 4 секунды задержка\n3. 4 секунды выдох\n4. Повторите 5 раз.\n\nДышите спокойно и осознанно.",
            "en": "🌬️ **Breathing (2 min)**\n\n1. Inhale for 4 seconds\n2. Hold for 4 seconds\n3. Exhale for 4 seconds\n4. Repeat 5 times.\n\nBreathe slowly and stay present."
        }
        await safe_edit(query, texts.get(lang, texts["en"]), reply_markup=get_back_home_keyboard(), parse_mode="Markdown")
        return

    if query.data == "meditate_calm":
        texts = {
            "uz": "🧘 **Tinchlanish (5 daq)**\n\n1. Qulay o'tiring\n2. Ko'zingizni yuming\n3. Nafasingizni kuzating\n4. Kelgan fikrlarni sudlamang, shunchaki qo'yib yuboring.",
            "ru": "🧘 **Спокойствие (5 мин)**\n\n1. Сядьте удобно\n2. Закройте глаза\n3. Наблюдайте за дыханием\n4. Мысли не оценивайте, просто отпускайте.",
            "en": "🧘 **Calm (5 min)**\n\n1. Sit comfortably\n2. Close your eyes\n3. Watch your breath\n4. Don’t judge thoughts, just let them pass."
        }
        await safe_edit(query, texts.get(lang, texts["en"]), reply_markup=get_back_home_keyboard(), parse_mode="Markdown")
        return

    if query.data == "meditate_sleep":
        texts = {
            "uz": "😴 **Uyquga tayyorgarlik (10 daq)**\n\n1. Yotib, tanangizni bo‘shating\n2. Nafasingizni sekinlashtiring\n3. Har bir mushakni navbatma-navbat bo‘sh qo‘ying\n4. Fikrlar kelib ketsa ham, ularga yopishib olmang.\n\n🌙 Yoqimli tushlar!",
            "ru": "😴 **Подготовка ко сну (10 мин)**\n\n1. Лягте и расслабьте тело\n2. Замедлите дыхание\n3. Поочередно расслабляйте мышцы\n4. Мысли пусть приходят и уходят.\n\n🌙 Сладких снов!",
            "en": "😴 **Sleep wind-down (10 min)**\n\n1. Lie down and relax your body\n2. Slow down your breathing\n3. Gently relax each muscle group\n4. Let thoughts come and go.\n\n🌙 Sweet dreams!"
        }
        await safe_edit(query, texts.get(lang, texts["en"]), reply_markup=get_back_home_keyboard(), parse_mode="Markdown")
        return

    if query.data == "stats":
        stats = get_user_stats(user_id)
        workout_count = get_workout_count(user_id)
        if stats["mood_count"] > 0:
            mood_emoji = ["😢", "😔", "😐", "🙂", "😄"][min(4, int(stats["avg_mood"]) - 1)]
            avg_line = f"{get_text(lang, 'stats_avg')}: {mood_emoji} ({stats['avg_mood']:.1f}/5)"
        else:
            avg_line = ""

        text = (
            f"📊 *{get_text(lang, 'stats_title')}*\n\n"
            f"{get_text(lang, 'stats_moods')}: *{stats['mood_count']}*\n"
            f"{get_text(lang, 'stats_journals')}: *{stats['journal_count']}*\n"
            f"{get_workout_stats_label(lang)}: *{workout_count}*\n"
        )
        if avg_line:
            text += f"{avg_line}\n"

        text += f"\n{get_text(lang, 'stats_tip')}"
        await safe_edit(query, text, reply_markup=get_back_home_keyboard(), parse_mode="Markdown")
        return

    if query.data == "chat":
        await safe_edit(query, get_text(lang, "chat_start"), reply_markup=get_back_home_keyboard())
        return

    if query.data == "help":
        base_help = get_text(lang, "help")
        text = f"❓ *Yordam*\n\n{base_help}\n\n" \
               "💡 *Tip:* Menga savol, muammo yoki his-tuyg'ularingizni yozishingiz mumkin."
        await safe_edit(query, text, reply_markup=get_back_home_keyboard(), parse_mode="Markdown")
        return

    if query.data == "lang":
        keyboard = [
            [InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz")],
            [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
            [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
            [InlineKeyboardButton("🏠 Bosh menyu", callback_data="home")],
        ]
        await safe_edit(
            query,
            get_text(lang, "lang_ask"),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

# === XABAR HANDLER ===

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text
    lang = get_user_lang(user_id)
    
    if context.user_data.get("waiting_for") == "journal":
        save_journal(user_id, user_message)
        context.user_data["waiting_for"] = None
        await update.message.reply_text(get_text(lang, "journal_saved"), reply_markup=get_back_home_keyboard())
        return
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    response = await get_ai_response(user_id, user_message)
    await update.message.reply_text(response, reply_markup=get_back_home_keyboard())

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
    app.add_handler(CommandHandler("fitness", fitness_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("reset", reset_command))
    app.add_handler(CommandHandler("lang", lang_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("✅ MindMate bot ishga tushdi!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
