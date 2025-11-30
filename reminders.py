# reminders.py - MindMate Eslatmalar Tizimi (13 til)

from datetime import datetime, time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# === REMINDER TEXTS (13 LANGUAGES) ===

REMINDER_TEXTS = {
    "uz": {
        "reminder_menu": "⏰ **Eslatmalar**\n\nQaysi eslatmalarni sozlamoqchisiz?",
        "mood_reminder": "😊 Kayfiyat",
        "meditate_reminder": "🧘 Meditatsiya",
        "workout_reminder": "💪 Mashq",
        "water_reminder": "💧 Suv",
        "my_reminders": "📋 Eslatmalarim",
        "set_time": "🕐 Vaqtni tanlang:",
        "reminder_set": "✅ Eslatma saqlandi! Har kuni **{time}** da eslataman.",
        "reminder_deleted": "🗑️ Eslatma o'chirildi.",
        "no_reminders": "📭 Eslatmalar yo'q.",
        "your_reminders": "📋 **Eslatmalaringiz:**\n\n",
        "mood_notify": "👋 Salom! Bugun kayfiyatingiz qanday?",
        "meditate_notify": "🧘 Meditatsiya vaqti! Bir oz tinchlanish vaqti.",
        "workout_notify": "💪 Mashq vaqti! Tanangizni harakatga keltiring!",
        "water_notify": "💧 Suv ichish vaqti! Sog'lom bo'ling.",
    },
    "ru": {
        "reminder_menu": "⏰ **Напоминания**\n\nКакие напоминания настроить?",
        "mood_reminder": "😊 Настроение",
        "meditate_reminder": "🧘 Медитация",
        "workout_reminder": "💪 Тренировка",
        "water_reminder": "💧 Вода",
        "my_reminders": "📋 Мои напоминания",
        "set_time": "🕐 Выберите время:",
        "reminder_set": "✅ Напоминание сохранено! Буду напоминать в **{time}**.",
        "reminder_deleted": "🗑️ Напоминание удалено.",
        "no_reminders": "📭 Напоминаний нет.",
        "your_reminders": "📋 **Ваши напоминания:**\n\n",
        "mood_notify": "👋 Привет! Как ваше настроение?",
        "meditate_notify": "🧘 Время медитации!",
        "workout_notify": "💪 Время тренировки!",
        "water_notify": "💧 Время пить воду!",
    },
    "en": {
        "reminder_menu": "⏰ **Reminders**\n\nWhich reminders to set?",
        "mood_reminder": "😊 Mood",
        "meditate_reminder": "🧘 Meditation",
        "workout_reminder": "💪 Workout",
        "water_reminder": "💧 Water",
        "my_reminders": "📋 My reminders",
        "set_time": "🕐 Select time:",
        "reminder_set": "✅ Reminder saved! I'll remind you at **{time}**.",
        "reminder_deleted": "🗑️ Reminder deleted.",
        "no_reminders": "📭 No reminders.",
        "your_reminders": "📋 **Your reminders:**\n\n",
        "mood_notify": "👋 Hi! How are you feeling?",
        "meditate_notify": "🧘 Meditation time!",
        "workout_notify": "💪 Workout time!",
        "water_notify": "💧 Time to drink water!",
    },
    "tr": {
        "reminder_menu": "⏰ **Hatırlatıcılar**\n\nHangi hatırlatıcıları ayarlayalım?",
        "mood_reminder": "😊 Ruh Hali",
        "meditate_reminder": "🧘 Meditasyon",
        "workout_reminder": "💪 Antrenman",
        "water_reminder": "💧 Su",
        "my_reminders": "📋 Hatırlatıcılarım",
        "set_time": "🕐 Saat seçin:",
        "reminder_set": "✅ Hatırlatıcı kaydedildi! **{time}**'da hatırlatacağım.",
        "reminder_deleted": "🗑️ Hatırlatıcı silindi.",
        "no_reminders": "📭 Hatırlatıcı yok.",
        "your_reminders": "📋 **Hatırlatıcılarınız:**\n\n",
        "mood_notify": "👋 Merhaba! Nasıl hissediyorsunuz?",
        "meditate_notify": "🧘 Meditasyon zamanı!",
        "workout_notify": "💪 Antrenman zamanı!",
        "water_notify": "💧 Su içme zamanı!",
    },
    "ar": {
        "reminder_menu": "⏰ **التذكيرات**\n\nأي تذكيرات تريد ضبطها؟",
        "mood_reminder": "😊 المزاج",
        "meditate_reminder": "🧘 التأمل",
        "workout_reminder": "💪 التمرين",
        "water_reminder": "💧 الماء",
        "my_reminders": "📋 تذكيراتي",
        "set_time": "🕐 اختر الوقت:",
        "reminder_set": "✅ تم حفظ التذكير! سأذكرك في **{time}**.",
        "reminder_deleted": "🗑️ تم حذف التذكير.",
        "no_reminders": "📭 لا توجد تذكيرات.",
        "your_reminders": "📋 **تذكيراتك:**\n\n",
        "mood_notify": "👋 مرحباً! كيف حالك اليوم؟",
        "meditate_notify": "🧘 وقت التأمل!",
        "workout_notify": "💪 وقت التمرين!",
        "water_notify": "💧 وقت شرب الماء!",
    },
    "hi": {
        "reminder_menu": "⏰ **रिमाइंडर**\n\nकौन से रिमाइंडर सेट करें?",
        "mood_reminder": "😊 मूड",
        "meditate_reminder": "🧘 ध्यान",
        "workout_reminder": "💪 व्यायाम",
        "water_reminder": "💧 पानी",
        "my_reminders": "📋 मेरे रिमाइंडर",
        "set_time": "🕐 समय चुनें:",
        "reminder_set": "✅ रिमाइंडर सेव हो गया! **{time}** पर याद दिलाऊंगा।",
        "reminder_deleted": "🗑️ रिमाइंडर हटाया गया।",
        "no_reminders": "📭 कोई रिमाइंडर नहीं।",
        "your_reminders": "📋 **आपके रिमाइंडर:**\n\n",
        "mood_notify": "👋 नमस्ते! आज कैसा महसूस कर रहे हैं?",
        "meditate_notify": "🧘 ध्यान का समय!",
        "workout_notify": "💪 व्यायाम का समय!",
        "water_notify": "💧 पानी पीने का समय!",
    },
    "zh": {
        "reminder_menu": "⏰ **提醒**\n\n设置哪些提醒？",
        "mood_reminder": "😊 心情",
        "meditate_reminder": "🧘 冥想",
        "workout_reminder": "💪 锻炼",
        "water_reminder": "💧 喝水",
        "my_reminders": "📋 我的提醒",
        "set_time": "🕐 选择时间：",
        "reminder_set": "✅ 提醒已保存！我会在 **{time}** 提醒你。",
        "reminder_deleted": "🗑️ 提醒已删除。",
        "no_reminders": "📭 没有提醒。",
        "your_reminders": "📋 **你的提醒：**\n\n",
        "mood_notify": "👋 你好！今天感觉怎么样？",
        "meditate_notify": "🧘 冥想时间！",
        "workout_notify": "💪 锻炼时间！",
        "water_notify": "💧 喝水时间！",
    },
    "ko": {
        "reminder_menu": "⏰ **알림**\n\n어떤 알림을 설정할까요?",
        "mood_reminder": "😊 기분",
        "meditate_reminder": "🧘 명상",
        "workout_reminder": "💪 운동",
        "water_reminder": "💧 물",
        "my_reminders": "📋 내 알림",
        "set_time": "🕐 시간 선택:",
        "reminder_set": "✅ 알림이 저장되었습니다! **{time}**에 알려드릴게요.",
        "reminder_deleted": "🗑️ 알림이 삭제되었습니다.",
        "no_reminders": "📭 알림이 없습니다.",
        "your_reminders": "📋 **알림 목록:**\n\n",
        "mood_notify": "👋 안녕하세요! 오늘 기분이 어떠세요?",
        "meditate_notify": "🧘 명상 시간입니다!",
        "workout_notify": "💪 운동 시간입니다!",
        "water_notify": "💧 물 마실 시간입니다!",
    },
    "ja": {
        "reminder_menu": "⏰ **リマインダー**\n\nどのリマインダーを設定しますか？",
        "mood_reminder": "😊 気分",
        "meditate_reminder": "🧘 瞑想",
        "workout_reminder": "💪 運動",
        "water_reminder": "💧 水",
        "my_reminders": "📋 マイリマインダー",
        "set_time": "🕐 時間を選択：",
        "reminder_set": "✅ リマインダーを保存しました！**{time}**にお知らせします。",
        "reminder_deleted": "🗑️ リマインダーを削除しました。",
        "no_reminders": "📭 リマインダーがありません。",
        "your_reminders": "📋 **リマインダー一覧：**\n\n",
        "mood_notify": "👋 こんにちは！今日の気分はいかがですか？",
        "meditate_notify": "🧘 瞑想の時間です！",
        "workout_notify": "💪 運動の時間です！",
        "water_notify": "💧 水を飲む時間です！",
    },
    "es": {
        "reminder_menu": "⏰ **Recordatorios**\n\n¿Qué recordatorios configurar?",
        "mood_reminder": "😊 Ánimo",
        "meditate_reminder": "🧘 Meditación",
        "workout_reminder": "💪 Ejercicio",
        "water_reminder": "💧 Agua",
        "my_reminders": "📋 Mis recordatorios",
        "set_time": "🕐 Selecciona hora:",
        "reminder_set": "✅ ¡Recordatorio guardado! Te recordaré a las **{time}**.",
        "reminder_deleted": "🗑️ Recordatorio eliminado.",
        "no_reminders": "📭 No hay recordatorios.",
        "your_reminders": "📋 **Tus recordatorios:**\n\n",
        "mood_notify": "👋 ¡Hola! ¿Cómo te sientes?",
        "meditate_notify": "🧘 ¡Hora de meditar!",
        "workout_notify": "💪 ¡Hora de ejercicio!",
        "water_notify": "💧 ¡Hora de beber agua!",
    },
    "fr": {
        "reminder_menu": "⏰ **Rappels**\n\nQuels rappels configurer?",
        "mood_reminder": "😊 Humeur",
        "meditate_reminder": "🧘 Méditation",
        "workout_reminder": "💪 Exercice",
        "water_reminder": "💧 Eau",
        "my_reminders": "📋 Mes rappels",
        "set_time": "🕐 Choisir l'heure:",
        "reminder_set": "✅ Rappel enregistré! Je vous rappellerai à **{time}**.",
        "reminder_deleted": "🗑️ Rappel supprimé.",
        "no_reminders": "📭 Aucun rappel.",
        "your_reminders": "📋 **Vos rappels:**\n\n",
        "mood_notify": "👋 Bonjour! Comment vous sentez-vous?",
        "meditate_notify": "🧘 C'est l'heure de méditer!",
        "workout_notify": "💪 C'est l'heure de l'exercice!",
        "water_notify": "💧 C'est l'heure de boire de l'eau!",
    },
    "de": {
        "reminder_menu": "⏰ **Erinnerungen**\n\nWelche Erinnerungen einrichten?",
        "mood_reminder": "😊 Stimmung",
        "meditate_reminder": "🧘 Meditation",
        "workout_reminder": "💪 Training",
        "water_reminder": "💧 Wasser",
        "my_reminders": "📋 Meine Erinnerungen",
        "set_time": "🕐 Zeit wählen:",
        "reminder_set": "✅ Erinnerung gespeichert! Ich erinnere dich um **{time}**.",
        "reminder_deleted": "🗑️ Erinnerung gelöscht.",
        "no_reminders": "📭 Keine Erinnerungen.",
        "your_reminders": "📋 **Deine Erinnerungen:**\n\n",
        "mood_notify": "👋 Hallo! Wie fühlst du dich?",
        "meditate_notify": "🧘 Zeit für Meditation!",
        "workout_notify": "💪 Zeit für Training!",
        "water_notify": "💧 Zeit Wasser zu trinken!",
    },
    "pt": {
        "reminder_menu": "⏰ **Lembretes**\n\nQuais lembretes configurar?",
        "mood_reminder": "😊 Humor",
        "meditate_reminder": "🧘 Meditação",
        "workout_reminder": "💪 Exercício",
        "water_reminder": "💧 Água",
        "my_reminders": "📋 Meus lembretes",
        "set_time": "🕐 Escolher horário:",
        "reminder_set": "✅ Lembrete salvo! Vou lembrar você às **{time}**.",
        "reminder_deleted": "🗑️ Lembrete excluído.",
        "no_reminders": "📭 Sem lembretes.",
        "your_reminders": "📋 **Seus lembretes:**\n\n",
        "mood_notify": "👋 Olá! Como você está se sentindo?",
        "meditate_notify": "🧘 Hora da meditação!",
        "workout_notify": "💪 Hora do exercício!",
        "water_notify": "💧 Hora de beber água!",
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

# === REMINDER TYPE INFO (13 LANGUAGES) ===

REMINDER_TYPES = {
    "mood": {
        "emoji": "😊",
        "name_uz": "Kayfiyat", "name_ru": "Настроение", "name_en": "Mood",
        "name_tr": "Ruh Hali", "name_ar": "المزاج", "name_hi": "मूड",
        "name_zh": "心情", "name_ko": "기분", "name_ja": "気分",
        "name_es": "Ánimo", "name_fr": "Humeur", "name_de": "Stimmung", "name_pt": "Humor"
    },
    "meditate": {
        "emoji": "🧘",
        "name_uz": "Meditatsiya", "name_ru": "Медитация", "name_en": "Meditation",
        "name_tr": "Meditasyon", "name_ar": "التأمل", "name_hi": "ध्यान",
        "name_zh": "冥想", "name_ko": "명상", "name_ja": "瞑想",
        "name_es": "Meditación", "name_fr": "Méditation", "name_de": "Meditation", "name_pt": "Meditação"
    },
    "workout": {
        "emoji": "💪",
        "name_uz": "Mashq", "name_ru": "Тренировка", "name_en": "Workout",
        "name_tr": "Antrenman", "name_ar": "التمرين", "name_hi": "व्यायाम",
        "name_zh": "锻炼", "name_ko": "운동", "name_ja": "運動",
        "name_es": "Ejercicio", "name_fr": "Exercice", "name_de": "Training", "name_pt": "Exercício"
    },
    "water": {
        "emoji": "💧",
        "name_uz": "Suv", "name_ru": "Вода", "name_en": "Water",
        "name_tr": "Su", "name_ar": "الماء", "name_hi": "पानी",
        "name_zh": "喝水", "name_ko": "물", "name_ja": "水",
        "name_es": "Agua", "name_fr": "Eau", "name_de": "Wasser", "name_pt": "Água"
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