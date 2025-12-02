"""
Financial AI Coach
Moliyaviy savodsizlikni hal qilish - xarajatlar, jamg'arish, investitsiya
"""

import logging
from datetime import datetime
from openai import OpenAI
import os

logger = logging.getLogger(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === FINANCIAL CATEGORIES ===

EXPENSE_CATEGORIES = {
    "uz": {
        "food": "🍽️ Ovqat",
        "transport": "🚗 Transport",
        "housing": "🏠 Uy-joy",
        "utilities": "💡 Kommunal",
        "healthcare": "🏥 Sog'liq",
        "education": "📚 Ta'lim",
        "entertainment": "🎬 O'yin-kulgi",
        "shopping": "🛍️ Xaridlar",
        "savings": "💰 Jamg'arma",
        "other": "📦 Boshqa"
    },
    "en": {
        "food": "🍽️ Food",
        "transport": "🚗 Transport",
        "housing": "🏠 Housing",
        "utilities": "💡 Utilities",
        "healthcare": "🏥 Healthcare",
        "education": "📚 Education",
        "entertainment": "🎬 Entertainment",
        "shopping": "🛍️ Shopping",
        "savings": "💰 Savings",
        "other": "📦 Other"
    }
}

# === DATABASE ===

def init_financial_tables(conn):
    """Moliyaviy jadvallar"""
    cur = conn.cursor()

    # Expenses
    cur.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            amount DECIMAL(10,2),
            currency TEXT DEFAULT 'UZS',
            category TEXT,
            description TEXT,
            date DATE DEFAULT CURRENT_DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Income
    cur.execute('''
        CREATE TABLE IF NOT EXISTS income (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            amount DECIMAL(10,2),
            currency TEXT DEFAULT 'UZS',
            source TEXT,
            description TEXT,
            date DATE DEFAULT CURRENT_DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Financial goals
    cur.execute('''
        CREATE TABLE IF NOT EXISTS financial_goals (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            goal_name TEXT,
            target_amount DECIMAL(10,2),
            current_amount DECIMAL(10,2) DEFAULT 0,
            currency TEXT DEFAULT 'UZS',
            deadline DATE,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Budget plans
    cur.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            user_id BIGINT,
            category TEXT,
            monthly_limit DECIMAL(10,2),
            currency TEXT DEFAULT 'UZS',
            PRIMARY KEY (user_id, category)
        )
    ''')

    conn.commit()
    cur.close()
    logger.info("✅ Financial tables initialized")


# === EXPENSE TRACKING ===

def add_expense(conn, user_id, amount, category, description="", currency="UZS"):
    """Xarajat qo'shish"""
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO expenses (user_id, amount, category, description, currency)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    ''', (user_id, amount, category, description, currency))
    expense_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    return expense_id


def add_income(conn, user_id, amount, source, description="", currency="UZS"):
    """Daromad qo'shish"""
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO income (user_id, amount, source, description, currency)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    ''', (user_id, amount, source, description, currency))
    income_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    return income_id


def get_monthly_summary(conn, user_id):
    """Oylik moliyaviy xulosа"""
    cur = conn.cursor()

    # Total expenses this month
    cur.execute('''
        SELECT COALESCE(SUM(amount), 0) FROM expenses
        WHERE user_id = %s
        AND date >= DATE_TRUNC('month', CURRENT_DATE)
    ''', (user_id,))
    total_expenses = float(cur.fetchone()[0])

    # Total income this month
    cur.execute('''
        SELECT COALESCE(SUM(amount), 0) FROM income
        WHERE user_id = %s
        AND date >= DATE_TRUNC('month', CURRENT_DATE)
    ''', (user_id,))
    total_income = float(cur.fetchone()[0])

    # Expenses by category
    cur.execute('''
        SELECT category, SUM(amount) FROM expenses
        WHERE user_id = %s
        AND date >= DATE_TRUNC('month', CURRENT_DATE)
        GROUP BY category
        ORDER BY SUM(amount) DESC
    ''', (user_id,))
    expenses_by_category = {row[0]: float(row[1]) for row in cur.fetchall()}

    cur.close()

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "balance": total_income - total_expenses,
        "expenses_by_category": expenses_by_category
    }


# === AI FINANCIAL ADVICE ===

async def get_financial_advice(user_id, conn, question, lang="en"):
    """AI financial advice"""
    try:
        # Get user's financial data
        summary = get_monthly_summary(conn, user_id)

        context = f"""You are a professional Financial Coach.

User's financial data (this month):
- Income: ${summary['total_income']:,.2f}
- Expenses: ${summary['total_expenses']:,.2f}
- Balance: ${summary['balance']:,.2f}

Expenses by category:
{chr(10).join([f"- {cat}: ${amt:,.2f}" for cat, amt in summary['expenses_by_category'].items()])}

User's question: {question}

Please provide advice following these guidelines:
1. Analyze the situation
2. Give specific recommendations (with numbers)
3. Suggest an action plan
4. Provide motivation

Answer should be clear and easy to understand."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional financial coach. Speak in clear and simple language."},
                {"role": "user", "content": context}
            ],
            max_tokens=800,
            temperature=0.7
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Financial advice error: {e}")
        return "⚠️ An error occurred. Please try again."


async def analyze_spending_habits(user_id, conn, lang="en"):
    """Analyze spending habits"""
    try:
        summary = get_monthly_summary(conn, user_id)

        if summary['total_expenses'] == 0:
            return "📊 No expenses recorded yet. Use /add_expense to add an expense."

        prompt = f"""Financial Analysis:

This month's data:
- Income: ${summary['total_income']:,.2f}
- Expenses: ${summary['total_expenses']:,.2f}
- Balance: ${summary['balance']:,.2f}

Expense breakdown:
{chr(10).join([f"- {cat}: ${amt:,.2f} ({amt/summary['total_expenses']*100:.1f}%)" for cat, amt in summary['expenses_by_category'].items()])}

Please analyze:
1. Are the expenses healthy?
2. Which category has the most spending?
3. Saving opportunities
4. 3 specific recommendations

Answer with emojis in clear and simple language."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.6
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Spending analysis error: {e}")
        return "⚠️ Tahlil qilishda xatolik."


async def create_budget_plan(user_id, conn, monthly_income, lang="uz"):
    """Byudjet rejasi yaratish"""
    try:
        prompt = f"""Oylik daromad: {monthly_income:,.0f} so'm

50/30/20 qoidasi asosida byudjet rejasi yarating:
- 50% - zarur xarajatlar (uy, ovqat, transport)
- 30% - ixtiyoriy (o'yin-kulgi, xaridlar)
- 20% - jamg'arma va investitsiya

Har bir kategoriya uchun aniq summalar va maslahatlar bering.
O'zbek tilida, emoji va jadval formatida."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.6
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Budget plan error: {e}")
        return "⚠️ Byudjet yaratishda xatolik."


# === INVESTMENT ADVICE ===

async def get_investment_advice(amount, risk_level, duration, lang="uz"):
    """Investitsiya maslahati"""
    try:
        prompt = f"""Investitsiya parametrlari:
- Summa: {amount:,.0f} so'm
- Risk darajasi: {risk_level}
- Muddat: {duration}

O'zbekiston sharoitida quyidagilarni taklif qiling:
1. Bank depozitlari
2. Ko'chmas mulk
3. Biznes
4. Kriptovalyuta (agar risk yuqori bo'lsa)
5. Diversifikatsiya strategiyasi

Har bir variant uchun:
- Kutilgan foyda
- Xavf darajasi
- Minimal summa
- Maslahatlar

O'zbek tilida, oddiy va tushunarli."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.7
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Investment advice error: {e}")
        return "⚠️ Maslahat olishda xatolik."


# === SMART ALERTS ===

def check_budget_alerts(conn, user_id):
    """Byudjet ogohlantirishlari"""
    cur = conn.cursor()

    alerts = []

    # Check each budget category
    cur.execute('''
        SELECT b.category, b.monthly_limit, COALESCE(SUM(e.amount), 0) as spent
        FROM budgets b
        LEFT JOIN expenses e ON b.user_id = e.user_id
            AND b.category = e.category
            AND e.date >= DATE_TRUNC('month', CURRENT_DATE)
        WHERE b.user_id = %s
        GROUP BY b.category, b.monthly_limit
    ''', (user_id,))

    for category, limit, spent in cur.fetchall():
        percentage = (spent / limit * 100) if limit > 0 else 0

        if percentage >= 90:
            alerts.append({
                "type": "critical",
                "message": f"🚨 {category}: {percentage:.0f}% ({spent:,.0f}/{limit:,.0f})"
            })
        elif percentage >= 75:
            alerts.append({
                "type": "warning",
                "message": f"⚠️ {category}: {percentage:.0f}% ({spent:,.0f}/{limit:,.0f})"
            })

    cur.close()
    return alerts


# === LANGUAGE TEXTS ===

def get_financial_texts(lang="uz"):
    """Moliyaviy matnlar"""
    return {
        "uz": {
            "menu": """💰 **Moliyaviy Coach**

Nima yordam kerak?""",
            "add_expense_prompt": "💸 Xarajat summasini kiriting (masalan: 50000):",
            "add_income_prompt": "💵 Daromad summasini kiriting:",
            "category_select": "📂 Kategoriyani tanlang:",
            "expense_added": "✅ Xarajat saqlandi: {amount:,.0f} so'm ({category})",
            "income_added": "✅ Daromad saqlandi: {amount:,.0f} so'm",
            "monthly_report": """📊 **Oylik Hisobot**

💵 Daromad: {income:,.0f} so'm
💸 Xarajat: {expenses:,.0f} so'm
💰 Balans: {balance:,.0f} so'm

📈 Xarajatlar:
{breakdown}

{advice}"""
        }
    }.get(lang, {})
