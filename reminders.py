# reminders.py - MindMate Eslatmalar Tizimi

from datetime import datetime, time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# === REMINDER TEXTS ===

REMINDER_TEXTS = {
    "uz": {
        "reminder_menu": "⏰ **Eslatmalar**\n\nQaysi eslatmalarni sozlamoqchisiz?",
        "mood_reminder": "😊 Kayfiyat eslatmasi",
        "meditate_reminder": "🧘 Meditatsiya eslatmasi",
        "workout_reminder": "💪 Mashq eslatmasi",
        "water_reminder": "💧 Suv ichish eslatmasi",
        "my_reminders": "📋 Mening eslatmalarim",
        "set_time": "🕐 Vaqtni tanlang:",
        "reminder_set": "✅ Eslatma saqlandi! Har kuni soat **{time}** da eslataman.",
        "reminder_deleted": "🗑️ Eslatma o'chirildi.",
        "no_reminders": "📭 Hali eslatmalar yo'q.",
        "your_reminders": "📋 **Sizning eslatmalaringiz:**\n\n",
        
        # Eslatma xabarlari
        "mood_notify": "👋 Salom! Bugun kayfiyatingiz qanday?\n\nKayfiyatingizni belgilang:",
        "meditate_notify": "🧘 Meditatsiya vaqti!\n\nBir necha daqiqa tinchlanish uchun vaqt ajrating.",
        "workout_notify": "💪 Mashq vaqti!\n\nTanangizni harakatga keltiring!",
        "water_notify": "💧 Suv ichish vaqti!\n\nSog'lom bo'lish uchun suv iching.",
    },
    "ru": {
        "reminder_menu": "⏰ **Напоминания**\n\nКакие напоминания хотите настроить?",
        "mood_reminder": "😊 Напоминание о настроении",
        "meditate_reminder": "🧘 Напоминание о медитации",
        "workout_reminder": "💪 Напоминание о тренировке",
        "water_reminder": "💧 Напоминание о воде",
        "my_reminders": "📋 Мои напоминания",
        "set_time": "🕐 Выберите время:",
        "reminder_set": "✅ Напоминание сохранено! Буду напоминать каждый день в **{time}**.",
        "reminder_deleted": "🗑️ Напоминание удалено.",
        "no_reminders": "📭 Напоминаний пока нет.",
        "your_reminders": "📋 **Ваши напоминания:**\n\n",
        
        "mood_notify": "👋 Привет! Как ваше настроение сегодня?\n\nОтметьте своё настроение:",
        "meditate_notify": "🧘 Время медитации!\n\nУделите несколько минут для расслабления.",
        "workout_notify": "💪 Время тренировки!\n\nПриведите тело в движение!",
        "water_notify": "💧 Время пить воду!\n\nПейте воду для здоровья.",
    },
    "en": {
        "reminder_menu": "⏰ **Reminders**\n\nWhich reminders would you like to set?",
        "mood_reminder": "😊 Mood reminder",
        "meditate_reminder": "🧘 Meditation reminder",
        "workout_reminder": "💪 Workout reminder",
        "water_reminder": "💧 Water reminder",
        "my_reminders": "📋 My reminders",
        "set_time": "🕐 Select time:",
        "reminder_set": "✅ Reminder saved! I'll remind you every day at **{time}**.",
        "reminder_deleted": "🗑️ Reminder deleted.",
        "no_reminders": "📭 No reminders yet.",
        "your_reminders": "📋 **Your reminders:**\n\n",
        
        "mood_notify": "👋 Hi! How are you feeling today?\n\nRate your mood:",
        "meditate_notify": "🧘 Meditation time!\n\nTake a few minutes to relax.",
        "workout_notify": "💪 Workout time!\n\nGet your body moving!",
        "water_notify": "💧 Time to drink water!\n\nStay hydrated for good health.",
    }
}

def get_reminder_text(lang, key):
    """Eslatma matnini olish"""
    if lang not in REMINDER_TEXTS:
        lang = "uz"
    return REMINDER_TEXTS[lang].get(key, REMINDER_TEXTS["uz"].get(key, ""))

# === REMINDER KEYBOARDS ===

def get_reminder_menu_keyboard(lang):
    """Eslatmalar menyu klaviaturasi"""
    texts = REMINDER_TEXTS.get(lang, REMINDER_TEXTS["uz"])
    keyboard = [
        [InlineKeyboardButton(texts["mood_reminder"], callback_data="remind_mood"),
         InlineKeyboardButton(texts["meditate_reminder"], callback_data="remind_meditate")],
        [InlineKeyboardButton(texts["workout_reminder"], callback_data="remind_workout"),
         InlineKeyboardButton(texts["water_reminder"], callback_data="remind_water")],
        [InlineKeyboardButton(texts["my_reminders"], callback_data="remind_list")],
        [InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_time_keyboard(reminder_type):
    """Vaqt tanlash klaviaturasi"""
    keyboard = [
        [InlineKeyboardButton("06:00", callback_data=f"rtime_{reminder_type}_06:00"),
         InlineKeyboardButton("07:00", callback_data=f"rtime_{reminder_type}_07:00"),
         InlineKeyboardButton("08:00", callback_data=f"rtime_{reminder_type}_08:00")],
        [InlineKeyboardButton("09:00", callback_data=f"rtime_{reminder_type}_09:00"),
         InlineKeyboardButton("10:00", callback_data=f"rtime_{reminder_type}_10:00"),
         InlineKeyboardButton("12:00", callback_data=f"rtime_{reminder_type}_12:00")],
        [InlineKeyboardButton("14:00", callback_data=f"rtime_{reminder_type}_14:00"),
         InlineKeyboardButton("18:00", callback_data=f"rtime_{reminder_type}_18:00"),
         InlineKeyboardButton("20:00", callback_data=f"rtime_{reminder_type}_20:00")],
        [InlineKeyboardButton("21:00", callback_data=f"rtime_{reminder_type}_21:00"),
         InlineKeyboardButton("22:00", callback_data=f"rtime_{reminder_type}_22:00")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="reminders"),
         InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_mood_keyboard_for_reminder():
    """Eslatma uchun kayfiyat klaviaturasi"""
    keyboard = [
        [InlineKeyboardButton("😄 Zo'r (5)", callback_data="mood_5"),
         InlineKeyboardButton("🙂 Yaxshi (4)", callback_data="mood_4")],
        [InlineKeyboardButton("😐 Normal (3)", callback_data="mood_3"),
         InlineKeyboardButton("😔 Yomon (2)", callback_data="mood_2")],
        [InlineKeyboardButton("😢 Juda yomon (1)", callback_data="mood_1")]
    ]
    return InlineKeyboardMarkup(keyboard)

# === REMINDER TYPE INFO ===

REMINDER_TYPES = {
    "mood": {
        "emoji": "😊",
        "name_uz": "Kayfiyat",
        "name_ru": "Настроение", 
        "name_en": "Mood"
    },
    "meditate": {
        "emoji": "🧘",
        "name_uz": "Meditatsiya",
        "name_ru": "Медитация",
        "name_en": "Meditation"
    },
    "workout": {
        "emoji": "💪",
        "name_uz": "Mashq",
        "name_ru": "Тренировка",
        "name_en": "Workout"
    },
    "water": {
        "emoji": "💧",
        "name_uz": "Suv",
        "name_ru": "Вода",
        "name_en": "Water"
    }
}

def get_reminder_type_name(reminder_type, lang):
    """Eslatma turi nomini olish"""
    info = REMINDER_TYPES.get(reminder_type, {})
    name_key = f"name_{lang}"
    return info.get(name_key, info.get("name_uz", reminder_type))

def get_reminder_emoji(reminder_type):
    """Eslatma turi emojisini olish"""
    return REMINDER_TYPES.get(reminder_type, {}).get("emoji", "⏰")

def format_reminder_list(reminders, lang):
    """Eslatmalar ro'yxatini formatlash"""
    if not reminders:
        return get_reminder_text(lang, "no_reminders")
    
    text = get_reminder_text(lang, "your_reminders")
    for r in reminders:
        emoji = get_reminder_emoji(r["type"])
        name = get_reminder_type_name(r["type"], lang)
        text += f"{emoji} **{name}** - {r['time']}\n"
    
    return text