"""
Enhanced Features: Optimized menus, referral system, quick expenses
Created based on user feedback
"""

import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton as IKB

logger = logging.getLogger(__name__)

# === OPTIMIZED MENUS ===

def get_ai_friend_menu(lang="en"):
    """AI Friend - Chat + Journal + Healer combined"""
    button_texts = {
        "en": {
            "chat": "💬 Chat",
            "journal": "📝 Journal",
            "healer": "🌿 Natural Healer",
            "mood": "😊 Mood",
            "deep_talk": "💭 Deep Talk",
            "main_menu": "🏠 Main Menu"
        },
        "ru": {
            "chat": "💬 Общаться",
            "journal": "📝 Дневник",
            "healer": "🌿 Природный Целитель",
            "mood": "😊 Настроение",
            "deep_talk": "💭 Глубокий разговор",
            "main_menu": "🏠 Главное меню"
        },
        "uz": {
            "chat": "💬 Suhbat",
            "journal": "📝 Kundalik",
            "healer": "🌿 Tabiy Shifokor",
            "mood": "😊 Kayfiyat",
            "deep_talk": "💭 Chuqur suhbat",
            "main_menu": "🏠 Bosh menyu"
        }
    }
    btn = button_texts.get(lang, button_texts["en"])
    keyboard = [
        [IKB(btn["chat"], callback_data="chat_mode"),
         IKB(btn["journal"], callback_data="journal_mode")],
        [IKB(btn["healer"], callback_data="healer")],
        [IKB(btn["mood"], callback_data="mood"),
         IKB(btn["deep_talk"], callback_data="deep_chat")],
        [IKB(btn["main_menu"], callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_health_menu(lang="en"):
    """Health - Meditation + Fitness + Health"""
    button_texts = {
        "en": {
            "meditation": "🧘 Meditation",
            "fitness": "💪 Fitness",
            "health_ai": "🏥 Health AI",
            "reminders": "⏰ Reminders",
            "main_menu": "🏠 Main Menu"
        },
        "ru": {
            "meditation": "🧘 Медитация",
            "fitness": "💪 Фитнес",
            "health_ai": "🏥 Здоровье AI",
            "reminders": "⏰ Напоминания",
            "main_menu": "🏠 Главное меню"
        },
        "uz": {
            "meditation": "🧘 Meditatsiya",
            "fitness": "💪 Fitness",
            "health_ai": "🏥 Salomatlik AI",
            "reminders": "⏰ Eslatmalar",
            "main_menu": "🏠 Bosh menyu"
        }
    }
    btn = button_texts.get(lang, button_texts["en"])
    keyboard = [
        [IKB(btn["meditation"], callback_data="meditate"),
         IKB(btn["fitness"], callback_data="fitness")],
        [IKB(btn["health_ai"], callback_data="health_ai"),
         IKB(btn["reminders"], callback_data="reminders")],
        [IKB(btn["main_menu"], callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_creative_tools_menu(lang="en"):
    """Creative tools - PDF, PPT, AI tools"""
    button_texts = {
        "en": {
            "create_pdf": "📄 Create PDF",
            "presentation": "📊 Presentation",
            "generate_image": "🎨 Generate Image",
            "write_code": "👨‍💻 Write Code",
            "translate": "🌐 Translate",
            "study": "📚 Study",
            "travel": "✈️ Travel",
            "recipe": "🍳 Recipe",
            "main_menu": "🏠 Main Menu"
        },
        "ru": {
            "create_pdf": "📄 Создать PDF",
            "presentation": "📊 Презентация",
            "generate_image": "🎨 Создать изображение",
            "write_code": "👨‍💻 Написать код",
            "translate": "🌐 Перевести",
            "study": "📚 Учёба",
            "travel": "✈️ Путешествие",
            "recipe": "🍳 Рецепт",
            "main_menu": "🏠 Главное меню"
        },
        "uz": {
            "create_pdf": "📄 PDF yaratish",
            "presentation": "📊 Prezentatsiya",
            "generate_image": "🎨 Rasm yaratish",
            "write_code": "👨‍💻 Kod yozish",
            "translate": "🌐 Tarjima",
            "study": "📚 O'qish",
            "travel": "✈️ Sayohat",
            "recipe": "🍳 Retsept",
            "main_menu": "🏠 Bosh menyu"
        }
    }
    btn = button_texts.get(lang, button_texts["en"])
    keyboard = [
        [IKB(btn["create_pdf"], callback_data="create_pdf"),
         IKB(btn["presentation"], callback_data="create_ppt")],
        [IKB(btn["generate_image"], callback_data="ai_image"),
         IKB(btn["write_code"], callback_data="ai_code")],
        [IKB(btn["translate"], callback_data="ai_translate"),
         IKB(btn["study"], callback_data="ai_study")],
        [IKB(btn["travel"], callback_data="ai_travel"),
         IKB(btn["recipe"], callback_data="ai_recipe")],
        [IKB(btn["main_menu"], callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_my_profile_menu(user_stats, lang="en"):
    """My Profile - Stats + Settings"""
    button_texts = {
        "en": {
            "statistics": "📊 Statistics",
            "goals": "🎯 Goals",
            "achievements": "🏆 Achievements",
            "progress": "📈 Progress",
            "main_menu": "🏠 Main Menu"
        },
        "ru": {
            "statistics": "📊 Статистика",
            "goals": "🎯 Цели",
            "achievements": "🏆 Достижения",
            "progress": "📈 Прогресс",
            "main_menu": "🏠 Главное меню"
        },
        "uz": {
            "statistics": "📊 Statistika",
            "goals": "🎯 Maqsadlar",
            "achievements": "🏆 Yutuqlar",
            "progress": "📈 Progress",
            "main_menu": "🏠 Bosh menyu"
        }
    }
    btn = button_texts.get(lang, button_texts["en"])
    keyboard = [
        [IKB(btn["statistics"], callback_data="stats"),
         IKB(btn["goals"], callback_data="goals")],
        [IKB(btn["achievements"], callback_data="achievements"),
         IKB(btn["progress"], callback_data="progress")],
        [IKB(btn["main_menu"], callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


# Removed get_settings_menu - now defined in main.py with proper language support


# === QUICK EXPENSE SHORTCUTS ===

def get_quick_expense_shortcuts(user_id, conn):
    """
    Quick buttons for frequently used expenses

    Args:
        user_id: User ID
        conn: Database connection

    Returns:
        List of frequent expenses with amounts
    """
    cur = conn.cursor()

    # Most frequently repeated expenses in the last 30 days
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

    keyboard.append([IKB("➕ Add Other Expense", callback_data="add_expense")])
    keyboard.append([IKB("🏠 Main Menu", callback_data="main_menu")])

    return InlineKeyboardMarkup(keyboard)


def add_recurring_expense(conn, user_id, category, amount, description, frequency="monthly"):
    """
    Add recurring expense (rent, internet, etc.)

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
    """Automatically add recurring expenses (check daily)"""
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

    # Bot username - should be obtained from .env
    bot_username = "MindMateAIBot"  # TODO: Add to .env
    ref_link = f"https://t.me/{bot_username}?start={ref_code}"

    keyboard = [
        [IKB("📤 Forward to Friend", switch_inline_query=f"Try MindMate bot! {ref_link}")],
        [IKB("📋 Copy Link", callback_data=f"copy_ref_{ref_code}")],
        [IKB("🎁 My Bonuses", callback_data="my_referral_bonuses")],
        [IKB("🔙 Back", callback_data="premium_menu")]
    ]

    return InlineKeyboardMarkup(keyboard)


def get_referral_text(user_id, ref_count, bonuses, lang="en"):
    """Referral text"""
    from premium import get_referral_code
    ref_code = get_referral_code(user_id)

    text = f"""🎁 **Invite Your Friends!**

👥 You've invited {ref_count} friends

🎉 **Your bonuses:**
• +{bonuses['ai_requests']} AI requests
• +{bonuses['pdf_bonus']} PDFs
• +{bonuses['premium_days']} days Premium

💰 **For each friend:**
• You: +5 AI requests, +2 PDFs
• Your friend: +3 AI requests, +1 PDF

📱 **How to share:**
1. "📤 Forward to Friend" - directly in Telegram
2. "📋 Copy Link" - share anywhere

🔗 Your referral code: `{ref_code}`"""

    return text


# === INVESTMENT IMPROVEMENTS ===

def get_investment_disclaimer():
    """Investment disclaimer"""
    return """⚠️ **IMPORTANT WARNING:**

📌 **This advice is for informational purposes only!**

• Consult with a professional financial advisor
• Do your own research
• Only invest money you can afford to lose
• High return = High risk
• Diversify (don't put all eggs in one basket)
• Create a long-term strategy

💡 **Note:** This is AI advice, not a professional advisor!

✅ Continue?"""


def get_premium_investment_features():
    """Premium investment features list"""
    return {
        "free": {
            "advice_count": 3,  # 3 consultations per month
            "detail_level": "basic",
            "features": ["General advice", "Risk assessment", "Basic diversification"]
        },
        "premium": {
            "advice_count": 20,
            "detail_level": "advanced",
            "features": [
                "Detailed analysis",
                "Personal portfolio recommendations",
                "Monthly market review",
                "Real-time alerts",
                "Tax optimization tips"
            ]
        },
        "pro": {
            "advice_count": -1,  # Unlimited
            "detail_level": "expert",
            "features": [
                "Professional-level analysis",
                "1-on-1 consultation (via AI)",
                "Custom investment strategies",
                "Advanced risk management",
                "Portfolio rebalancing suggestions",
                "Referral to real professionals"
            ]
        }
    }


# === AI FRIEND (CHAT + JOURNAL COMBINED) ===

def get_ai_friend_prompt(user_memories, mood_history, lang="en"):
    """
    AI Friend - real friend who talks, listens, and analyzes
    """
    prompt = f"""You are a real friend and psychologist speaking in {lang.upper()}.

🎯 **YOUR ROLES:**

1. **LISTENING FRIEND:**
   - Sincere and caring
   - Non-judgmental
   - Shows empathy
   - Understanding and supportive

2. **SMART ADVISOR:**
   - Provides practical solutions
   - Motivates
   - Analyzes problems
   - Inspires

3. **PERSONAL PSYCHOLOGIST:**
   - Tracks mood changes
   - Sees patterns
   - Understands through questions
   - Suggests professional help when needed

📚 **ABOUT THE USER:**
{user_memories}

📊 **MOOD HISTORY:**
{mood_history}

💬 **HOW TO TALK:**
• Simple, clear language
• Use emojis (but not too many)
• Ask questions - to learn
• Connect with reality
• Give hope and strength
• Address problems, but guide to positive solutions

🚫 **DON'T:**
• Make medical diagnoses
• Recommend medications
• Be too formal
• Write long responses
• Just listen passively - actively engage

✨ **GOAL:** Be the best friend who truly understands and helps the user!"""

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
