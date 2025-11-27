import os
import logging
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
client = OpenAI(api_key=OPENAI_API_KEY)

# Ma'lumotlar saqlash
user_data = {}

def get_user_data(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            "conversations": [],
            "moods": [],
            "journals": [],
            "language": "uz"
        }
    return user_data[user_id]

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
    data = get_user_data(user_id)
    
    if len(data["conversations"]) == 0:
        data["conversations"].append({"role": "system", "content": SYSTEM_PROMPT})
    
    data["conversations"].append({"role": "user", "content": message})
    
    if len(data["conversations"]) > 21:
        data["conversations"] = [data["conversations"][0]] + data["conversations"][-20:]
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=data["conversations"],
            max_tokens=500,
            temperature=0.7
        )
        ai_message = response.choices[0].message.content
        data["conversations"].append({"role": "assistant", "content": ai_message})
        return ai_message
    except Exception as e:
        logger.error(f"OpenAI xatosi: {e}")
        return "Kechirasiz, hozir javob bera olmayapman. Keyinroq urinib ko'ring."

# === BUYRUQLAR ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    data = get_user_data(user_id)
    
    mood_count = len(data["moods"])
    journal_count = len(data["journals"])
    
    if mood_count > 0:
        avg_mood = sum(m["score"] for m in data["moods"]) / mood_count
        mood_emoji = ["😢", "😔", "😐", "🙂", "😄"][min(4, int(avg_mood) - 1)]
    else:
        avg_mood = 0
        mood_emoji = "❓"
    
    stats_text = f"""
📊 **Sizning statistikangiz**

😊 Kayfiyat yozuvlari: {mood_count}
📝 Kundalik yozuvlari: {journal_count}
{f"📈 O'rtacha kayfiyat: {mood_emoji} ({avg_mood:.1f}/5)" if mood_count > 0 else ""}

💡 Har kuni kayfiyatingizni belgilang va kundalik yozing!
    """
    await update.message.reply_text(stats_text, parse_mode="Markdown")

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_data:
        user_data[user_id]["conversations"] = []
    await update.message.reply_text("🔄 Suhbat yangilandi!")

# === CALLBACK HANDLER ===

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = get_user_data(user_id)
    
    if query.data.startswith("mood_"):
        score = int(query.data.split("_")[1])
        data["moods"].append({"score": score, "date": datetime.now().isoformat()})
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
        mood_count = len(data["moods"])
        journal_count = len(data["journals"])
        if mood_count > 0:
            avg_mood = sum(m["score"] for m in data["moods"]) / mood_count
            mood_emoji = ["😢", "😔", "😐", "🙂", "😄"][min(4, int(avg_mood) - 1)]
        else:
            avg_mood = 0
            mood_emoji = "❓"
        
        stats_text = f"""
📊 **Sizning statistikangiz**

😊 Kayfiyat yozuvlari: {mood_count}
📝 Kundalik yozuvlari: {journal_count}
{f"📈 O'rtacha kayfiyat: {mood_emoji} ({avg_mood:.1f}/5)" if mood_count > 0 else ""}
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
    data = get_user_data(user_id)
    
    # Kundalik kutayotgan bo'lsa
    if context.user_data.get("waiting_for") == "journal":
        data["journals"].append({
            "text": user_message,
            "date": datetime.now().isoformat()
        })
        context.user_data["waiting_for"] = None
        await update.message.reply_text(
            "✅ Kundalik saqlandi!\n\n💬 Fikrlaringiz haqida gaplashmqchimisiz?"
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