import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# .env fayldan o'zgaruvchilarni yuklash
load_dotenv()

# Logging sozlash
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API kalitlarni olish
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAI clientni yaratish
client = OpenAI(api_key=OPENAI_API_KEY)

# Foydalanuvchilar suhbat tarixi
conversations = {}

# AI javob olish funksiyasi
async def get_ai_response(user_id: int, message: str) -> str:
    """OpenAI dan javob olish"""
    
    # Foydalanuvchi tarixini olish yoki yangi yaratish
    if user_id not in conversations:
        conversations[user_id] = [
            {
                "role": "system",
                "content": """Sen MindMate - mehribon va tushunuvchi AI psixologsan. 
                Sening vazifang odamlarga ruhiy yordam berish, ularni tinglash va qo'llab-quvvatlash.
                
                Qoidalar:
                - Har doim o'zbek tilida gapir
                - Mehribon va samimiy bo'l
                - Hukm qilma, faqat qo'llab-quvvatla
                - Oddiy va tushunarli so'zlar ishlar
                - Kerak bo'lsa, professional yordamga yo'naltir
                """
            }
        ]
    
    # Yangi xabarni qo'shish
    conversations[user_id].append({"role": "user", "content": message})
    
    try:
        # OpenAI dan javob olish
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=conversations[user_id],
            max_tokens=500,
            temperature=0.7
        )
        
        ai_message = response.choices[0].message.content
        
        # AI javobini tarixga qo'shish
        conversations[user_id].append({"role": "assistant", "content": ai_message})
        
        # Tarixni 20 ta xabar bilan cheklash
        if len(conversations[user_id]) > 21:
            conversations[user_id] = [conversations[user_id][0]] + conversations[user_id][-20:]
        
        return ai_message
        
    except Exception as e:
        logger.error(f"OpenAI xatosi: {e}")
        return "Kechirasiz, hozir javob bera olmayapman. Iltimos, keyinroq urinib ko'ring."

# /start buyrug'i
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Botni boshlash"""
    welcome_message = """
🌟 Salom! Men MindMate - sizning shaxsiy AI yordamchingizman.

Men sizga yordam bera olaman:
- Stressni yengillashtirish
- His-tuyg'ularingizni tushunish
- Kundalik muammolarni hal qilish
- Motivatsiya va qo'llab-quvvatlash

💬 Menga istalgan narsani yozishingiz mumkin. Men sizni tinglayman va yordam berishga harakat qilaman.

Boshlash uchun shunchaki xabar yozing!
    """
    await update.message.reply_text(welcome_message)

# /help buyrug'i
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yordam xabari"""
    help_text = """
📚 MindMate yordam:

/start - Botni qayta boshlash
/help - Ushbu yordam xabari
/reset - Suhbatni yangilash

💡 Maslahat: Menga o'zingizni qanday his qilayotganingizni yozing, men sizga yordam berishga harakat qilaman.
    """
    await update.message.reply_text(help_text)

# /reset buyrug'i
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Suhbat tarixini tozalash"""
    user_id = update.effective_user.id
    if user_id in conversations:
        del conversations[user_id]
    await update.message.reply_text("🔄 Suhbat yangilandi. Qaytadan boshlashingiz mumkin!")

# Oddiy xabarlarni qayta ishlash
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi xabarlarini qayta ishlash"""
    user_id = update.effective_user.id
    user_message = update.message.text
    
    # "Yozmoqda..." holati
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # AI dan javob olish
    response = await get_ai_response(user_id, user_message)
    
    # Javobni yuborish
    await update.message.reply_text(response)

# Asosiy funksiya
def main():
    """Botni ishga tushirish"""
    
    # Token tekshirish
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN topilmadi!")
        return
    
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY topilmadi!")
        return
    
    # Application yaratish
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Handlerlarni qo'shish
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Botni ishga tushirish
    logger.info("✅ MindMate bot ishga tushdi!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()