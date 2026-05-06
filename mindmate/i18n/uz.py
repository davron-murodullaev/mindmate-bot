"""
Uzbek translations
"""

TRANSLATIONS = {
    "welcome": "👋 MindMate'ga xush kelibsiz!\n\nMen sizning ruhiy salomatlik va samaradorlik uchun AI yordamchingizman.\n\nIltimos, tilingizni tanlang:",

    "setup": {
        "complete": "✅ Sozlash tugallandi! Endi barcha funksiyalardan foydalanishingiz mumkin.",
        "choose_timezone": "Iltimos, vaqt zonangizni tanlang:",
    },

    "menu": {
        "main_menu": "🏠 Asosiy menyu\n\nBugun nima qilmoqchisiz?",
        "mood_tracking": "😊 Kayfiyat",
        "healer": "🌟 Shifokor",
        "journal": "📝 Kundalik",
        "productivity": "🎯 Samaradorlik",
        "reminders": "⏰ Eslatmalar",
        "stats": "📊 Statistika",
        "settings": "⚙️ Sozlamalar",
        "premium": "💎 Premium",
        "help": "❓ Yordam",
    },

    "mood": {
        "select": "Bugun o'zingizni qanday his qilyapsiz?",
        "logged": "✅ Kayfiyat saqlandi!",
        "happy": "Xursand",
        "sad": "G'amgin",
        "angry": "Jahldor",
        "anxious": "Tashvishli",
        "tired": "Charchagan",
        "excited": "Hayajonli",
        "stats": "📊 So'nggi {days} kundagi kayfiyat statistikasi:",
        "no_data": "Hali kayfiyat ma'lumotlari yo'q. Birinchi kayfiyatingizni kiriting!",
    },

    "healer": {
        "welcome": "🌟 Shifokor rejimiga xush kelibsiz\n\nMen sizni tinglash va qo'llab-quvvatlash uchun shu yerdaman. Fikrlaringiz bilan bo'lishing.\n\nXabaringizni quyida yozing:",
        "active": "🌟 Shifokor rejimi faol\n\nMen tinglayapman. Fikr va his-tuyg'ularingiz bilan bo'lishing:",
        "exit": "Bo'lishganingiz uchun rahmat. O'zingizga yaxshilik qiling! 💚",
        "crisis": "Sizning hayotingiz qadrli. Iltimos, darhol professional yordamga murojaat qiling:\n\n🆘 Tez yordam:\n• 1050 (O'zbekiston ishonch telefoni)\n• 103 (Tez tibbiy yordam)\n\nYolg'iz emassiz. 💚",
    },

    "journal": {
        "welcome": "📝 Kundalik\n\nNima qilmoqchisiz?",
        "new_entry": "✍️ Yangi yozuv",
        "view_entries": "📖 Yozuvlarni ko'rish",
        "enter_text": "Kundalik yozuvingizni yozing:\n\n(Xohlaganingizcha yozishingiz mumkin)",
        "saved": "✅ Yozuv saqlandi!",
        "no_entries": "Sizda hali kundalik yozuvlari yo'q.",
        "entry": "📝 {date} dagi yozuv:\n\n{content}",
    },

    "productivity": {
        "welcome": "🎯 Samaradorlik murabbiysi\n\nMen sizga maqsadlaringizga erishish va samaradorlikni oshirishda yordam berish uchun shu yerdaman!\n\nBugun qanday yordam bera olaman?",
        "active": "🎯 Samaradorlik rejimi faol\n\nVazifalaringiz, maqsadlaringiz bilan bo'lishing yoki samaradorlik bo'yicha maslahat so'rang:",
    },

    "stats": {
        "welcome": "📊 Sizning statistikangiz\n\nNimani ko'rmoqchisiz?",
        "mood": "😊 Kayfiyat statistikasi",
        "journal": "📝 Kundalik statistikasi",
        "overall": "📈 Umumiy statistika",
        "summary": "📊 Umumiy statistika ({days} kun):\n\n• Kayfiyat yozuvlari: {moods}\n• Kundalik yozuvlari: {journals}\n• AI suhbatlar: {chats}",
    },

    "reminders": {
        "welcome": "⏰ Eslatmalar\n\nNima qilmoqchisiz?",
        "new": "➕ Yangi eslatma",
        "list": "📋 Mening eslatmalarim",
        "set": "⏰ Eslatma o'rnatish\n\nMenga qachon va nima haqida eslatishim kerakligini ayting.\n\nMisol: Ertaga soat 15:00 da suv ichishni eslatib tur",
        "created": "✅ Eslatma yaratildi!\n\nMen sizga eslataman: {text}\nVaqt: {time}",
        "notification": "⏰ Eslatma: {text}",
        "no_reminders": "Sizda faol eslatmalar yo'q.",
        "list_item": "• {time} — {text}",
        "limit_reached": "❌ Bepul rejimda maksimum {limit} eslatma mumkin. Premium'ga o'ting!",
        "parse_error": "❌ Vaqtni tushunmadim. Iltimos, qayta urinib ko'ring.\n\nMisol: Ertaga 15:00 da yig'ilish",
    },

    "settings": {
        "welcome": "⚙️ Sozlamalar",
        "language": "🌐 Til",
        "timezone": "🕐 Vaqt zonasi",
        "delete_data": "🗑 Ma'lumotlarimni o'chirish",
        "delete_confirm": "⚠️ Barcha ma'lumotlaringiz o'chiriladi. Davom etasizmi?",
        "delete_done": "✅ Ma'lumotlaringiz o'chirildi.",
    },

    "premium": {
        "welcome": "💎 Premium obuna\n\nPremium imkoniyatlar:\n\n✅ Cheksiz AI suhbatlar\n✅ Cheksiz eslatmalar\n✅ Chuqur statistika\n✅ Ovozli xabarlar\n✅ Birinchi navbatda javob\n\nNarxi: 25 000 so'm/oy",
        "subscribe_stars": "⭐ Telegram Stars (200⭐)",
        "subscribe_card": "💳 Karta orqali to'lash",
        "active": "✅ Premium obunangiz faol! Tugash sanasi: {date}",
        "limit_reached": "❌ Bugungi bepul limit tugadi ({limit} ta xabar). Premium'ga o'ting!",
    },

    "errors": {
        "generic": "❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.",
        "invalid_input": "❌ Noto'g'ri kirish. Qaytadan urinib ko'ring.",
        "database": "❌ Ma'lumotlar bazasi xatosi. Qo'llab-quvvatlash bilan bog'laning.",
        "ai_error": "❌ AI xizmati vaqtincha mavjud emas.",
    },

    "buttons": {
        "back": "⬅️ Orqaga",
        "cancel": "❌ Bekor qilish",
        "confirm": "✅ Tasdiqlash",
        "next": "➡️ Keyingi",
    },
}
