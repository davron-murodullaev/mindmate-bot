import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)
from openai import OpenAI
from languages import get_text, get_mood_response, TRANSLATIONS
from fitness import get_workout_text, get_workout_buttons, get_workout_done, get_workout_stats_label

# =====================================================
#                INITIAL SETUP
# =====================================================

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# =====================================================
#                MOCK DATABASE (TEMPORARY)
# =====================================================

# Har safar user uchun vaqtinchalik saqlash
USER_DATA = {}
CONVERSATIONS = {}
MOODS = {}
JOURNALS = {}
WORKOUTS = {}

def get_user_lang(user_id):
    return USER_DATA.get(user_id, {}).get("lang", "uz")

def set_user_lang(user_id, lang):
    USER_DATA.setdefault(user_id, {})["lang"] = lang

def save_user(user_id, username, lang="uz"):
    USER_DATA[user_id] = {"username": username, "lang": lang}

def save_mood(user_id, score, note=None):
    MOODS.setdefault(user_id, []).append(score)

def save_journal(user_id, text):
    JOURNALS.setdefault(user_id, []).append(text)

def get_user_stats(user_id):
    moods = MOODS.get(user_id, [])
    journals = JOURNALS.get(user_id, [])
    workouts = WORKOUTS.get(user_id, [])

    avg = sum(moods) / len(moods) if moods else 0

    return {
        "mood_count": len(moods),
        "avg_mood": avg,
        "journal_count": len(journals),
        "workout_count": len(workouts)
    }

def save_workout(user_id, workout_type):
    WORKOUTS.setdefault(user_id, []).append(workout_type)

def get_workout_count(user_id):
    return len(WORKOUTS.get(user_id, []))

def save_conversation(user_id, role, content):
    CONVERSATIONS.setdefault(user_id, []).append({"role": role, "content": content})
    CONVERSATIONS[user_id] = CONVERSATIONS[user_id][-20:]  # oxirgi 20 ta

def get_conversations(user_id):
    return CONVERSATIONS.get(user_id, [])

def clear_conversations(user_id):
    CONVERSATIONS[user_id] = []

# =====================================================
#                AI ENGINE
# =====================================================

def get_system_prompt(lang):
    prompts = {
        "uz": "Sen MindMate - mehribon AI psixolog. O'zbek tilida gapir. Qisqa, samimiy javob ber (3-5 gap).",
        "ru": "Ты MindMate - добрый AI психолог. Отвечай кратко, тепло (3-5 предложений).",
        "en": "You are MindMate - a kind AI psychologist. Speak warmly (3–5 sentences)."
    }
    return prompts.get(lang, prompts["en"])

async def get_ai_response(user_id: int, message: str) -> str:
    lang = get_user_lang(user_id)
    conv = get_conversations(user_id)

    messages = [{"role": "system", "content": get_system_prompt(lang)}]
    messages.extend(conv)
    messages.append({"role": "user", "content": message})

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=400,
            temperature=0.7
        )
        ai_msg = response.choices[0].message.content

        save_conversation(user_id, "user", message)
        save_conversation(user_id, "assistant", ai_msg)

        return ai_msg

    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        return "❗ Kechirasiz, AI hozir javob bera olmadi."

# =====================================================
#                COMMAND HANDLERS
# =====================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user.id, user.username)
    lang = get_user_lang(user.id)

    keyboard = [
        [InlineKeyboardButton(get_text(lang, "btn_mood"), callback_data="mood"),
         InlineKeyboardButton(get_text(lang, "btn_journal"), callback_data="journal")],
        [InlineKeyboardButton(get_text(lang, "btn_meditate"), callback_data="meditate"),
         InlineKeyboardButton("💪 Fitness", callback_data="fitness")],
        [InlineKeyboardButton(get_text(lang, "btn_stats"), callback_data="stats"),
         InlineKeyboardButton(get_text(lang, "btn_help"), callback_data="help")],
        [InlineKeyboardButton("🌍 Language", callback_data="lang")]
    ]

    await update.message.reply_text(
        get_text(lang, "welcome"),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_lang(update.effective_user.id)
    await update.message.reply_text(get_text(lang, "help"), parse_mode="Markdown")

# =====================================================
#                CALLBACK BUTTON HANDLER
# =====================================================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lang = get_user_lang(user_id)

    # Language change
    if query.data.startswith("lang_"):
        new_lang = query.data.split("_")[1]
        set_user_lang(user_id, new_lang)
        await query.edit_message_text(get_text(new_lang, "lang_changed"))
        return

    # Mood
    if query.data.startswith("mood_"):
        score = int(query.data.split("_")[1])
        save_mood(user_id, score)
        await query.edit_message_text(get_mood_response(lang, score))
        return

    # Journal
    if query.data == "journal":
        context.user_data["waiting_for"] = "journal"
        await query.edit_message_text(get_text(lang, "journal_ask"))
        return

    # Meditate menu
    if query.data == "meditate":
        keyboard = [
            [InlineKeyboardButton(get_text(lang, "meditate_breathing"), callback_data="meditate_breathing"),
             InlineKeyboardButton(get_text(lang, "meditate_calm"), callback_data="meditate_calm")],
            [InlineKeyboardButton(get_text(lang, "meditate_sleep"), callback_data="meditate_sleep")]
        ]
        await query.edit_message_text(get_text(lang, "meditate_ask"), reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # Fitness start
    if query.data == "fitness":
        btns = get_workout_buttons(lang)
        keyboard = [
            [InlineKeyboardButton(btns["morning"], callback_data="workout_morning"),
             InlineKeyboardButton(btns["energy"], callback_data="workout_energy")],
            [InlineKeyboardButton(btns["relax"], callback_data="workout_relax")]
        ]
        await query.edit_message_text(btns["ask"], reply_markup=InlineKeyboardMarkup(keyboard))
        return

# =====================================================
#                MESSAGE HANDLER
# =====================================================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    msg = update.message.text

    lang = get_user_lang(user_id)

    # Journal mode
    if context.user_data.get("waiting_for") == "journal":
        save_journal(user_id, msg)
        context.user_data["waiting_for"] = None
        await update.message.reply_text(get_text(lang, "journal_saved"))
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    ai = await get_ai_response(user_id, msg)
    await update.message.reply_text(ai)

# =====================================================
#                MAIN
# =====================================================

def main():
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN topilmadi!")
        return
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY topilmadi!")
        return

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🚀 MindMate bot ishga tushdi!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
