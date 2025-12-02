"""
Enhanced Features: Optimized menus, referral system, quick expenses
Foydalanuvchi feedbacklari asosida yaratilgan
"""

import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton as IKB

logger = logging.getLogger(__name__)

# === OPTIMIZED MENUS ===

def get_ai_friend_menu(lang="en"):
    """AI Friend - Chat + Journal + Healer combined (multilingual)"""
    texts = {
        "en": {
            "chat": "💬 Chat",
            "journal": "📝 Journal",
            "healer": "🌿 Natural Healer",
            "mood": "😊 Mood",
            "deep": "💭 Deep Talk",
            "home": "🏠 Home"
        },
        "uz": {
            "chat": "💬 Suhbatlashish",
            "journal": "📝 Kundalik",
            "healer": "🌿 Tabiiy Shifokor",
            "mood": "😊 Kayfiyat",
            "deep": "💭 Fikr almashish",
            "home": "🏠 Bosh menyu"
        }
    }
    t = texts.get(lang, texts["en"])

    keyboard = [
        [IKB(t["chat"], callback_data="chat_mode"),
         IKB(t["journal"], callback_data="journal_mode")],
        [IKB(t["healer"], callback_data="healer")],
        [IKB(t["mood"], callback_data="mood"),
         IKB(t["deep"], callback_data="deep_chat")],
        [IKB(t["home"], callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_health_menu(lang="en"):
    """Health - Meditation + Fitness + Health (multilingual)"""
    texts = {
        "en": {"med": "🧘 Meditation", "fit": "💪 Fitness", "health": "🏥 Health AI", "remind": "⏰ Reminders", "home": "🏠 Home"},
        "uz": {"med": "🧘 Meditatsiya", "fit": "💪 Fitness", "health": "🏥 Sog'liq AI", "remind": "⏰ Eslatmalar", "home": "🏠 Bosh menyu"}
    }
    t = texts.get(lang, texts["en"])
    keyboard = [
        [IKB(t["med"], callback_data="meditate"),
         IKB(t["fit"], callback_data="fitness")],
        [IKB(t["health"], callback_data="health_ai"),
         IKB(t["remind"], callback_data="reminders")],
        [IKB(t["home"], callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_creative_tools_menu(lang="en"):
    """Creative tools - PDF, PPT, AI tools (multilingual)"""
    texts = {
        "en": {"pdf": "📄 Create PDF", "ppt": "📊 Presentation", "img": "🎨 Generate Image", "code": "👨‍💻 Write Code",
               "translate": "🌐 Translate", "study": "📚 Study", "travel": "✈️ Travel", "recipe": "🍳 Recipe", "home": "🏠 Home"},
        "uz": {"pdf": "📄 PDF yaratish", "ppt": "📊 Prezentatsiya", "img": "🎨 Rasm yaratish", "code": "👨‍💻 Kod yozish",
               "translate": "🌐 Tarjima", "study": "📚 O'quv", "travel": "✈️ Sayohat", "recipe": "🍳 Retsept", "home": "🏠 Bosh menyu"}
    }
    t = texts.get(lang, texts["en"])
    keyboard = [
        [IKB(t["pdf"], callback_data="create_pdf"),
         IKB(t["ppt"], callback_data="create_ppt")],
        [IKB(t["img"], callback_data="ai_image"),
         IKB(t["code"], callback_data="ai_code")],
        [IKB(t["translate"], callback_data="ai_translate"),
         IKB(t["study"], callback_data="ai_study")],
        [IKB(t["travel"], callback_data="ai_travel"),
         IKB(t["recipe"], callback_data="ai_recipe")],
        [IKB(t["home"], callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_my_profile_menu(user_stats, lang="en"):
    """My Profile - Stats + Settings (multilingual)"""
    texts = {
        "en": {"stats": "📊 Statistics", "goals": "🎯 Goals", "achievements": "🏆 Achievements", "progress": "📈 Progress", "home": "🏠 Home"},
        "uz": {"stats": "📊 Statistika", "goals": "🎯 Maqsadlar", "achievements": "🏆 Yutuqlar", "progress": "📈 Progress", "home": "🏠 Bosh menyu"}
    }
    t = texts.get(lang, texts["en"])
    keyboard = [
        [IKB(t["stats"], callback_data="stats"),
         IKB(t["goals"], callback_data="goals")],
        [IKB(t["achievements"], callback_data="achievements"),
         IKB(t["progress"], callback_data="progress")],
        [IKB(t["home"], callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_settings_menu(lang="en"):
    """Settings (multilingual)"""
    texts = {
        "en": {"lang": "🌍 Language", "notif": "🔔 Notifications", "reset": "🔄 Clear History", "help": "ℹ️ Help", "home": "🏠 Home"},
        "uz": {"lang": "🌍 Til", "notif": "🔔 Bildirishnomalar", "reset": "🔄 Tarikhni tozalash", "help": "ℹ️ Yordam", "home": "🏠 Bosh menyu"}
    }
    t = texts.get(lang, texts["en"])
    keyboard = [
        [IKB(t["lang"], callback_data="lang"),
         IKB(t["notif"], callback_data="notifications")],
        [IKB(t["reset"], callback_data="reset_confirm"),
         IKB(t["help"], callback_data="help")],
        [IKB(t["home"], callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


# === QUICK EXPENSE SHORTCUTS ===

def get_quick_expense_shortcuts(user_id, conn):
    """
    Tez-tez ishlatiladigan xarajatlar uchun quick buttons

    Args:
        user_id: Foydalanuvchi ID
        conn: Database connection

    Returns:
        List of frequent expenses with amounts
    """
    cur = conn.cursor()

    # So'nggi 30 kundagi eng ko'p takrorlangan xarajatlar
    cur.execute('''
        SELECT category, ROUND(AVG(amount), 0) as avg_amount, COUNT(*) as frequency
        FROM expenses
        WHERE user_id = %s AND date >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY category
        HAVING COUNT(*) >= 3
        ORDER BY frequency DESC
        LIMIT 5
    ''', (user_id,))

    shortcuts = []
    for row in cur.fetchall():
        shortcuts.append({
            "category": row[0],
            "avg_amount": float(row[1]),
            "frequency": row[2]
        })

    cur.close()
    return shortcuts


def get_expense_shortcuts_keyboard(shortcuts):
    """Quick expense buttons"""
    keyboard = []

    category_emoji = {
        "food": "🍽️",
        "transport": "🚗",
        "housing": "🏠",
        "utilities": "💡",
        "shopping": "🛍️",
        "entertainment": "🎬",
        "other": "📦"
    }

    for sc in shortcuts:
        emoji = category_emoji.get(sc["category"], "📦")
        text = f"{emoji} {sc['category'].title()} ({sc['avg_amount']:,.0f})"
        keyboard.append([IKB(text, callback_data=f"quick_exp_{sc['category']}_{int(sc['avg_amount'])}")])

    keyboard.append([IKB("➕ Boshqa xarajat", callback_data="add_expense")])
    keyboard.append([IKB("🏠 Bosh menyu", callback_data="main_menu")])

    return InlineKeyboardMarkup(keyboard)


def add_recurring_expense(conn, user_id, category, amount, description, frequency="monthly"):
    """
    Doimiy xarajatni qo'shish (uy-ijara, internet, etc.)

    Args:
        frequency: daily, weekly, monthly
    """
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS recurring_expenses (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            category TEXT,
            amount DECIMAL(10,2),
            description TEXT,
            frequency TEXT,
            last_added DATE,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cur.execute('''
        INSERT INTO recurring_expenses (user_id, category, amount, description, frequency)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    ''', (user_id, category, amount, description, frequency))

    recurring_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    return recurring_id


def check_recurring_expenses(conn, user_id):
    """Doimiy xarajatlarni avtomatik qo'shish (har kuni tekshirish)"""
    cur = conn.cursor()

    cur.execute('''
        SELECT id, category, amount, description, frequency, last_added
        FROM recurring_expenses
        WHERE user_id = %s AND is_active = TRUE
    ''', (user_id,))

    from datetime import datetime, timedelta
    from financial_coach import add_expense

    for row in cur.fetchall():
        rec_id, category, amount, description, frequency, last_added = row

        should_add = False
        today = datetime.now().date()

        if not last_added:
            should_add = True
        elif frequency == "daily" and last_added < today:
            should_add = True
        elif frequency == "weekly" and (today - last_added).days >= 7:
            should_add = True
        elif frequency == "monthly" and (today - last_added).days >= 30:
            should_add = True

        if should_add:
            # Add expense
            add_expense(conn, user_id, amount, category, description)

            # Update last_added
            cur.execute('''
                UPDATE recurring_expenses SET last_added = CURRENT_DATE
                WHERE id = %s
            ''', (rec_id,))
            conn.commit()

    cur.close()


# === REFERRAL IMPROVEMENTS ===

def get_referral_share_keyboard(user_id, lang="uz"):
    """
    Referral ulashish - Forward button + Copy link
    """
    from premium import get_referral_code
    ref_code = get_referral_code(user_id)

    # Bot username - .env'dan olish kerak
    bot_username = "MindMateAIBot"  # TODO: .env'ga qo'shish
    ref_link = f"https://t.me/{bot_username}?start={ref_code}"

    keyboard = [
        [IKB("📤 Do'stga yuborish", switch_inline_query=f"MindMate botini sinab ko'ring! {ref_link}")],
        [IKB("📋 Link nusxalash", callback_data=f"copy_ref_{ref_code}")],
        [IKB("🎁 Bonuslarim", callback_data="my_referral_bonuses")],
        [IKB("🔙 Orqaga", callback_data="premium_menu")]
    ]

    return InlineKeyboardMarkup(keyboard)


def get_referral_text(user_id, ref_count, bonuses, lang="uz"):
    """Referral matn"""
    from premium import get_referral_code
    ref_code = get_referral_code(user_id)

    text = f"""🎁 **Do'stlaringizni taklif qiling!**

👥 Siz {ref_count} ta do'st taklif qildingiz

🎉 **Sizning bonuslaringiz:**
• +{bonuses['ai_requests']} ta AI so'rov
• +{bonuses['pdf_bonus']} ta PDF
• +{bonuses['premium_days']} kun Premium

💰 **Har bir do'st uchun:**
• Siz: +5 AI so'rov, +2 PDF
• Do'stingiz: +3 AI so'rov, +1 PDF

📱 **Qanday ulashish:**
1. "📤 Do'stga yuborish" - telegram'da to'g'ridan-to'g'ri
2. "📋 Link nusxalash" - istalgan joyga joylashtirish

🔗 Sizning referal kodingiz: `{ref_code}`"""

    return text


# === INVESTMENT IMPROVEMENTS ===

def get_investment_disclaimer():
    """Investment ogohlantirishi"""
    return """⚠️ **MUHIM OGOHLANTIRISH:**

📌 **Ushbu maslahatlar faqat ma'lumot uchun!**

• Professional moliyaviy maslahatchi bilan maslahatlashing
• O'z tadqiqotingizni o'tkazing
• Faqat yo'qotishga tayyor pulni investitsiya qiling
• Yuqori foyda = yuqori xavf
• Diversifikatsiya qiling (bir joyga hammasi yo'q)
• Uzoq muddatli strategiya tuzing

💡 **Eslatma:** Bu AI maslahat, professional maslahatchi emas!

✅ Davom etasizmi?"""


def get_premium_investment_features():
    """Premium investment features ro'yxati"""
    return {
        "free": {
            "advice_count": 3,  # Oyiga 3 ta maslahat
            "detail_level": "basic",
            "features": ["Umumiy maslahatlar", "Risk baholash", "Asosiy diversifikatsiya"]
        },
        "premium": {
            "advice_count": 20,
            "detail_level": "advanced",
            "features": [
                "Batafsil tahlil",
                "Shaxsiy portfolio tavsiyasi",
                "Oylik market review",
                "Real-time alerts",
                "Tax optimization tips"
            ]
        },
        "pro": {
            "advice_count": -1,  # Unlimited
            "detail_level": "expert",
            "features": [
                "Professional darajadagi tahlil",
                "1-on-1 maslahat (AI orqali)",
                "Custom investment strategies",
                "Advanced risk management",
                "Portfolio rebalancing suggestions",
                "Real professional'ga yo'naltirish"
            ]
        }
    }


# === AI FRIEND (CHAT + JOURNAL COMBINED) ===

def get_ai_friend_prompt(user_memories, mood_history, lang="uz"):
    """
    AI Do'st - haqiqiy do'stdek gaplashadigan, tinglaydigan, tahlil qiladigan
    """
    prompt = f"""Siz - {lang.upper()} tilida gapiradigan haqiqiy do'st va psixolog.

🎯 **SIZNING ROLLARINGIZ:**

1. **TINGLOVCHI DO'ST:**
   - Samimiy va g'amxo'r
   - Hukmga chiqarmaydi
   - Empatiya ko'rsatadi
   - Tushunadi va qo'llab-quvvatlaydi

2. **AQLLI MASLAHATCHI:**
   - Amaliy yechimlar beradi
   - Motivatsiya qiladi
   - Muammolarni tahlil qiladi
   - Ilhomlantiradi

3. **SHAXSIY PSIXOLOG:**
   - Kayfiyat o'zgarishlarini kuzatadi
   - Pattern'larni ko'radi
   - Savol-javob orqali tushunadi
   - Professional yordam kerakligini anglasa, aytadi

📚 **FOYDALANUVCHI HAQIDA:**
{user_memories}

📊 **KAYFIYAT TARIXI:**
{mood_history}

💬 **QANDAY GAPLASHISH:**
• Oddiy, tushunarli til
• Emoji ishlatish (lekin ko'p emas)
• Savol bering - o'rganish uchun
• Voqelik bilan bog'lang
• Umid va kuch bering
• Muammoga e'tibor, lekin ijobiy yechimga yo'naltiring

🚫 **QILMANG:**
• Tibbiy diagnoz qo'ymang
• Dori tavsiya qilmang
• Juda rasmiy bo'lmang
• Uzun-uzun javob yozmang
• Faqat eshitib qolmang, faol qatnashing

✨ **MAQSAD:** Foydalanuvchini chinakam tushunadigan va yordam beradigan eng yaxshi do'st bo'lish!"""

    return prompt


# === TEXTS ===

def get_menu_texts(lang="en"):
    """Updated menu texts (multilingual)"""
    texts = {
        "en": {
            "ai_friend": """💬 **AI Friend**

I'm your personal AI friend.
Chat, journal, get advice.

Everything is private and secure! ❤️""",
            "health": """🧘 **Health**

Everything for your mental and physical health:
• Meditation
• Fitness
• Health advice""",
            "creative": """🎨 **Creative Tools**

Create with AI:
• PDFs and Presentations
• Images
• Code
• And more!""",
            "profile": """📊 **My Profile**

Your results and achievements."""
        },
        "uz": {
            "ai_friend": """💬 **AI Do'st**

Men sizning shaxsiy AI do'stingizman.
Suhbatlashing, kundalik yozing, maslahat so'rang.

Hamma narsa maxfiy va xavfsiz! ❤️""",
            "health": """🧘 **Salomatlik**

Ruhiy va jismoniy salomatligingiz uchun hamma narsa:
• Meditatsiya
• Fitness
• Sog'liq maslahati""",
            "creative": """🎨 **Ijod Vositalari**

AI yordamida yarating:
• PDF va Prezentatsiyalar
• Rasmlar
• Kodlar
• Va boshqalar!""",
            "profile": """📊 **Mening Profilim**

Sizning natijalaringiz va yutuqlaringiz."""
        }
    }
    return texts.get(lang, texts["en"])
