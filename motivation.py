"""
Motivatsion xabarlar va kunlik ilhom
"""

import random
from datetime import datetime

DAILY_QUOTES = {
    "uz": [
        "🌟 Har bir yangi kun - yangi imkoniyat. Bugun o'zingizni g'amgin his qilsangiz ham, albatta yaxshi kun keladi!",
        "💪 Siz o'ylaganingizdan ham kuchliroqsiz. Qiyin kunlar sizni yanada kuchaytiради.",
        "🌈 Hayot chiroyli, chunki siz chiroylisiz. O'zingizni sev va baxtli bo'ling!",
        "⭐ Kichik qadamlar katta maqsadlarga olib boradi. Bugun bitta yaxshi ish qiling!",
        "🦋 O'zgarish - bu hayot. Qo'rqmang, yangi narsalarni sinab ko'ring!",
        "🌸 Sizning tabassum sizni va atrofingizdagilarni baxtli qiladi. Tabassum qiling!",
        "🎯 Maqsadingizga har kuni bir qadam yaqinlashib boring. Siz bunga qodirsiz!",
        "💎 Siz noyobsiz va qimmatlisiz. Buni hech qachon unutmang!",
        "🌺 Bugun o'zingiz uchun biror yaxshi narsa qiling. Siz bunga loyiqsiz!",
        "🔥 Ichingizda yonayotgan olov hech qachon so'nmasin. Orzu qiling va harakat qiling!",
    ],
    "ru": [
        "🌟 Каждый новый день - новая возможность. Даже если сегодня грустно, обязательно будет хороший день!",
        "💪 Вы сильнее, чем думаете. Трудные дни делают вас еще сильнее.",
        "🌈 Жизнь прекрасна, потому что вы прекрасны. Любите себя и будьте счастливы!",
        "⭐ Маленькие шаги ведут к большим целям. Сделайте одно хорошее дело сегодня!",
        "🦋 Изменения - это жизнь. Не бойтесь пробовать новое!",
        "🌸 Ваша улыбка делает счастливыми вас и окружающих. Улыбайтесь!",
        "🎯 Каждый день приближайтесь к своей цели на один шаг. Вы способны на это!",
        "💎 Вы уникальны и ценны. Никогда не забывайте об этом!",
        "🌺 Сегодня сделайте что-то хорошее для себя. Вы заслуживаете этого!",
        "🔥 Пусть огонь внутри вас никогда не гаснет. Мечтайте и действуйте!",
    ],
    "en": [
        "🌟 Every new day is a new opportunity. Even if today feels sad, a good day will surely come!",
        "💪 You are stronger than you think. Difficult days make you even stronger.",
        "🌈 Life is beautiful because you are beautiful. Love yourself and be happy!",
        "⭐ Small steps lead to big goals. Do one good thing today!",
        "🦋 Change is life. Don't be afraid to try new things!",
        "🌸 Your smile makes you and those around you happy. Smile!",
        "🎯 Get one step closer to your goal every day. You can do it!",
        "💎 You are unique and valuable. Never forget that!",
        "🌺 Do something good for yourself today. You deserve it!",
        "🔥 Let the fire inside you never go out. Dream and act!",
    ]
}

MOOD_ENCOURAGEMENT = {
    "uz": {
        1: [
            "😢 Tushunaman, hozir juda og'ir. Lekin bu ham o'tadi. Siz yolg'iz emassiz, men shu yerdaman.",
            "💙 Yig'lash - bu kuchlilik belgisi. O'zingizga vaqt bering, hammasi yaxshi bo'ladi.",
            "🤗 Qiyin payt ekan. Biror kishi bilan gaplashsangiz yaxshi bo'ladi. Men sizni tinglayman.",
        ],
        2: [
            "😔 Bugun yomon kun bo'ldi shekilli. Ertaga yaxshiroq bo'ladi, ishoning.",
            "🌤️ Quyosh hali ham bulutlar ortida. Tez orada ko'rinadi, sabr qiling.",
            "💚 O'zingizga g'amxo'rlik qiling. Issiq choy iching va dam oling.",
        ],
        3: [
            "😐 Normal kun. Ehtimol biror narsa bilan o'zingizni xursand qilsangiz?",
            "🎨 Bugun o'zingiz uchun biror yoqimli narsa qiling!",
            "🌟 Normal - bu yaxshi! Kichik quvonchlar topishga harakat qiling.",
        ],
        4: [
            "🙂 Yaxshi kayfiyat! Davom eting, ajoyib kun bo'ladi!",
            "✨ Bugungi yaxshi energiyani saqlang va ulashing!",
            "🎉 Zo'r! Sizning ijobiy kayfiyatingiz atrofingizdagilarga ham ta'sir qiladi.",
        ],
        5: [
            "😄 Ajoyib! Sizning baxtingiz meni ham xursand qiladi!",
            "🌈 Bugungi ajoyib kayfiyatingizni unutmang. Bu his yozib qo'ying!",
            "🎊 Fantastik! Siz yorqin nuringizni ulashib boring!",
        ]
    }
}

ACTIVITY_SUGGESTIONS = {
    "uz": {
        "sad": [
            "🎵 Sevimli musiqangizni tinglang",
            "📱 Yaqin do'stingizga qo'ng'iroq qiling",
            "🚶 Qisqa sayr qiling",
            "📝 His-tuyg'ularingizni yozing",
            "🎬 Yengil komediya tomosha qiling",
            "🛁 Issiq vanna qabul qiling",
        ],
        "stressed": [
            "🧘 5 daqiqa meditatsiya qiling",
            "💪 Qisqa jismoniy mashq qiling",
            "🌳 Tabiатga chiqing",
            "🎨 Chizish yoki ranglash",
            "📖 Kitob o'qing",
            "☕ Choy iching va dam oling",
        ],
        "happy": [
            "📸 Yaxshi lahzani suratga oling",
            "💌 Kimgadir rahmat aytish xati yozing",
            "🎵 Raqsga tushing!",
            "🤗 Kimnidir quchoqlang",
            "🎁 O'zingizga kichik sovg'a qiling",
            "✨ Bugungi yaxshi narsalarni yozib qo'ying",
        ]
    }
}

def get_daily_quote(lang="uz"):
    """Kunlik motivatsion xabar"""
    quotes = DAILY_QUOTES.get(lang, DAILY_QUOTES["uz"])
    # Kundan kelib chiqib, bir xil xabarni ko'rsatish
    today = datetime.now().timetuple().tm_yday
    index = today % len(quotes)
    return quotes[index]

def get_mood_encouragement(lang, mood_score):
    """Kayfiyatga mos rag'batlantirish"""
    encouragements = MOOD_ENCOURAGEMENT.get(lang, {}).get(mood_score, [])
    if encouragements:
        return random.choice(encouragements)
    return ""

def get_activity_suggestion(lang, mood_type):
    """Faoliyat takliflari"""
    suggestions = ACTIVITY_SUGGESTIONS.get(lang, {}).get(mood_type, [])
    if suggestions:
        return random.sample(suggestions, min(3, len(suggestions)))
    return []

def get_time_greeting(lang="uz"):
    """Vaqtga mos salom"""
    hour = datetime.now().hour

    greetings = {
        "uz": {
            "morning": "🌅 Xayrli tong! Yangi kun, yangi imkoniyatlar!",
            "afternoon": "☀️ Xayrli kun! Kun yaxshi o'tyaptimi?",
            "evening": "🌆 Xayrli kech! Dam olish vaqti keldi.",
            "night": "🌙 Xayrli kecha! Yaxshi dam oling va yoqimli tushlar ko'ring."
        },
        "ru": {
            "morning": "🌅 Доброе утро! Новый день, новые возможности!",
            "afternoon": "☀️ Добрый день! Как проходит день?",
            "evening": "🌆 Добрый вечер! Время отдыхать.",
            "night": "🌙 Доброй ночи! Хорошо отдохните и приятных снов."
        },
        "en": {
            "morning": "🌅 Good morning! New day, new opportunities!",
            "afternoon": "☀️ Good afternoon! How's your day going?",
            "evening": "🌆 Good evening! Time to relax.",
            "night": "🌙 Good night! Rest well and sweet dreams."
        }
    }

    if 5 <= hour < 12:
        time_key = "morning"
    elif 12 <= hour < 17:
        time_key = "afternoon"
    elif 17 <= hour < 22:
        time_key = "evening"
    else:
        time_key = "night"

    return greetings.get(lang, greetings["uz"])[time_key]
