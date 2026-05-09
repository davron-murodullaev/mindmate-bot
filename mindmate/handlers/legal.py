"""
/privacy and /terms commands — required for any bot that handles personal
data and especially for friend-finding / dating features.
"""
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from mindmate.services.user_service import user_service
from mindmate.i18n import t

logger = logging.getLogger(__name__)


PRIVACY_TEXT_UZ = """🔒 *Maxfiylik siyosati*

*Yangilangan:* 2026

*Biz qanday ma'lumotlarni yig'amiz?*
• Telegram ID, ism, til
• Anketa ma'lumotlari (yosh, shahar, qiziqishlar, rasm)
• AI suhbatlar (xizmatni yaxshilash uchun)
• Eslatma, kayfiyat, kundalik yozuvlari

*Qanday foydalanamiz?*
• Sizga AI javoblari va tavsiyalar berish
• Do'st topish bo'limida mos kelishlarni qidirish
• Bot funksiyalarini yaxshilash

*Uchinchi tomonlar:*
• OpenAI — AI javoblari uchun (anonim, sizning shaxsiy ma'lumotlaringizsiz)
• Telegram — xabar yuborish uchun
• Boshqa hech kim

*Sizning huquqlaringiz:*
• Ma'lumotlaringizni istalgan vaqt o'chirish (Sozlamalar → 🗑 Ma'lumotlarimni o'chirish)
• Anketani yashirish (Do'st topish → 🙈)
• Botdan chiqib ketish

*Aloqa:* @your_admin_username
"""


TERMS_TEXT_UZ = """📜 *Foydalanish shartlari*

*Botdan foydalanib, siz quyidagi shartlarga rozilik bildirasiz:*

1️⃣ *Yosh chegarasi:* Faqat 18 yoshdan oshgan foydalanuvchilar uchun

2️⃣ *Hurmat:* Hurmatsizlik, tahdid, nomaqbul kontent qat'iyan taqiqlanadi. AI avtomatik aniqlaydi va bloklaydi

3️⃣ *Halollik:* Soxta profil, taqlid, boshqa odamning rasmlaridan foydalanish taqiqlanadi

4️⃣ *AI maslahati:* Bot maslahat beradi, lekin professional psixolog, shifokor yoki advokat o'rnini bosa olmaydi

5️⃣ *Premium:* To'langan obuna pul qaytarilmaydi. Obuna avtomatik yangilanmaydi

6️⃣ *Mas'uliyat:* Bot foydalanuvchilar o'rtasidagi munosabatlar uchun mas'uliyat olmaydi

7️⃣ *O'zgarishlar:* Shartlar yangilanishi mumkin. Sezilarli o'zgarishlar haqida sizga xabar beriladi

*Aloqa:* @your_admin_username
"""


async def privacy_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/privacy command — show full privacy policy."""
    user = update.effective_user
    message = update.message
    try:
        lang = await user_service.get_user_language(user.id)
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📜 Foydalanish shartlari", callback_data="legal_terms")],
            [InlineKeyboardButton("⬅️ Asosiy menyu", callback_data="menu_main")],
        ])
        await message.reply_text(PRIVACY_TEXT_UZ, reply_markup=kb, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error in privacy_handler: {e}")
        await message.reply_text(PRIVACY_TEXT_UZ)


async def terms_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/terms command — show full terms of service."""
    user = update.effective_user
    message = update.message
    try:
        lang = await user_service.get_user_language(user.id)
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔒 Maxfiylik siyosati", callback_data="legal_privacy")],
            [InlineKeyboardButton("⬅️ Asosiy menyu", callback_data="menu_main")],
        ])
        await message.reply_text(TERMS_TEXT_UZ, reply_markup=kb, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error in terms_handler: {e}")
        await message.reply_text(TERMS_TEXT_UZ)


async def legal_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle legal_* callbacks (switch between privacy and terms views)."""
    query = update.callback_query
    try:
        await query.answer()
        data = query.data or ""
        if data == "legal_privacy":
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("📜 Foydalanish shartlari", callback_data="legal_terms")],
                [InlineKeyboardButton("⬅️ Asosiy menyu", callback_data="menu_main")],
            ])
            await query.edit_message_text(PRIVACY_TEXT_UZ, reply_markup=kb, parse_mode="Markdown")
        elif data == "legal_terms":
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔒 Maxfiylik siyosati", callback_data="legal_privacy")],
                [InlineKeyboardButton("⬅️ Asosiy menyu", callback_data="menu_main")],
            ])
            await query.edit_message_text(TERMS_TEXT_UZ, reply_markup=kb, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error in legal_callback: {e}")
