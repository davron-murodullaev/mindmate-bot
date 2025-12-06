"""
Uzbek translations
"""

TRANSLATIONS = {
    "welcome": "👋 MindMate'ga xush kelibsiz!\n\nMen sizning ruhiy salomatlik, samaradorlik va farovonlik uchun AI yordamchingizman.\n\nIltimos, tilingizni tanlang:",

    "setup": {
        "complete": "✅ Sozlash tugallandi! Endi barcha funksiyalardan foydalanishingiz mumkin.",
        "choose_timezone": "Iltimos, vaqt zonangizni tanlang:",
    },

    "menu": {
        "main_menu": "🏠 Asosiy menyu\n\nBugun nima qilmoqchisiz?",
        "mood_tracking": "😊 Kayfiyatni kuzatish",
        "meditation": "🧘 Meditatsiya",
        "fitness": "💪 Fitnes",
        "healer": "🌟 Shifokor bilan gaplashish",
        "journal": "📝 Kundalik",
        "productivity": "🎯 Samaradorlik",
        "finance": "💰 Moliya",
        "stats": "📊 Statistika",
        "settings": "⚙️ Sozlamalar",
        "help": "❓ Yordam",
    },

    "mood": {
        "select": "Bugun o'zingizni qanday his qilyapsiz?",
        "logged": "✅ Kayfiyat saqlandi!",
        "happy": "😊 Xursand",
        "sad": "😢 G'amgin",
        "angry": "😠 Jahldor",
        "anxious": "😰 Tashvishli",
        "tired": "😴 Charchagan",
        "excited": "🤗 Hayajonli",
        "stats": "📊 So'nggi {days} kundagi kayfiyat statistikasi:",
    },

    "meditation": {
        "welcome": "🧘 Meditatsiyaga xush kelibsiz\n\nMeditatsiya davomiyligini tanlang:",
        "duration_5": "5 daqiqa",
        "duration_10": "10 daqiqa",
        "duration_15": "15 daqiqa",
        "duration_20": "20 daqiqa",
        "duration_30": "30 daqiqa",
        "start": "🧘 {duration} daqiqalik meditatsiya boshlanmoqda...\n\nQulay holatni toping, ko'zlaringizni yuming va nafasingizga e'tibor qarating.\n\nSessiya tugagach, sizga xabar beraman.",
        "complete": "✅ Meditatsiya tugadi!\n\nAjoyib! Siz {duration} daqiqalik meditatsiyani tugatdingiz.",
        "stats": "📊 Meditatsiya statistikasi:\n\nJami sessiyalar: {total}\nUmumiy vaqt: {time} daqiqa\nO'rtacha davomiylik: {avg} daqiqa",
    },

    "fitness": {
        "welcome": "💪 Fitnes kuzatuvi\n\nNima qilmoqchisiz?",
        "log_workout": "📝 Mashg'ulotni yozish",
        "view_stats": "📊 Statistikani ko'rish",
        "enter_workout": "Mashg'ulot ma'lumotlarini quyidagi formatda kiriting:\n\nFaoliyat: davomiylik (daqiqa)\n\nMisol: Yugurish: 30",
        "logged": "✅ Mashg'ulot yozildi!\n\nFaoliyat: {activity}\nDavomiylik: {duration} daqiqa",
        "stats": "📊 Fitnes statistikasi ({days} kun):\n\nJami mashg'ulotlar: {total}\nUmumiy davomiylik: {duration} daqiqa\nO'rtacha davomiylik: {avg} daqiqa",
    },

    "healer": {
        "welcome": "🌟 Shifokor rejimiga xush kelibsiz\n\nMen sizni tinglash va qo'llab-quvvatlash uchun shu yerdaman. Fikrlaringiz bilan bo'lishing.\n\nXabaringizni quyida yozing:",
        "active": "🌟 Shifokor rejimi faol\n\nMen tinglayapman. Fikr va his-tuyg'ularingiz bilan bo'lishing:",
        "exit": "Bo'lishganingiz uchun rahmat. O'zingizga yaxshilik qiling! 💚",
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

    "finance": {
        "welcome": "💰 Moliya kuzatuvi\n\nNima qilmoqchisiz?",
        "add_expense": "➕ Xarajat qo'shish",
        "view_stats": "📊 Statistikani ko'rish",
        "enter_expense": "Xarajat ma'lumotlarini quyidagi formatda kiriting:\n\nMiqdor Kategoriya: Tavsif\n\nMisol: 50 oziq-ovqat: Restoranda tushlik",
        "added": "✅ Xarajat qo'shildi!\n\nMiqdor: ${amount}\nKategoriya: {category}",
        "stats": "📊 Moliya statistikasi ({days} kun):\n\nJami xarajatlar: ${total}\nO'rtacha xarajat: ${avg}\nTransaksiyalar soni: {count}",
        "by_category": "💰 Kategoriyalar bo'yicha xarajatlar:\n\n{categories}",
    },

    "stats": {
        "welcome": "📊 Sizning statistikangiz\n\nNimani ko'rmoqchisiz?",
        "mood": "😊 Kayfiyat statistikasi",
        "fitness": "💪 Fitnes statistikasi",
        "meditation": "🧘 Meditatsiya statistikasi",
        "finance": "💰 Moliya statistikasi",
        "overall": "📈 Umumiy statistika",
    },

    "reminders": {
        "set": "⏰ Eslatma o'rnatish\n\nMenga qachon va nima haqida eslatishim kerakligini ayting.\n\nMisol: Ertaga soat 15:00 da suv ichishni eslatib tur",
        "created": "✅ Eslatma yaratildi!\n\nMen sizga eslataman: {text}\nVaqt: {time}",
        "notification": "⏰ Eslatma: {text}",
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
