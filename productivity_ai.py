"""
Productivity & Time Management AI
Vaqt boshqaruvi, vazifalar, fokus, unumdorlik
"""

import logging
from datetime import datetime, timedelta
from openai import OpenAI
import os

logger = logging.getLogger(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === TASK PRIORITIES ===

PRIORITY_LEVELS = {
    "urgent": {"name": "🔴 Shoshilinch", "value": 4},
    "high": {"name": "🟠 Yuqori", "value": 3},
    "medium": {"name": "🟡 O'rta", "value": 2},
    "low": {"name": "🟢 Past", "value": 1}
}

# === DATABASE ===

def init_productivity_tables(conn):
    """Productivity jadvallar"""
    cur = conn.cursor()

    # Tasks
    cur.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            title TEXT,
            description TEXT,
            priority TEXT DEFAULT 'medium',
            category TEXT,
            due_date TIMESTAMP,
            estimated_minutes INTEGER,
            completed BOOLEAN DEFAULT FALSE,
            completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Focus sessions (Pomodoro)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS focus_sessions (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            task_id INTEGER REFERENCES tasks(id),
            duration_minutes INTEGER DEFAULT 25,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed BOOLEAN DEFAULT FALSE
        )
    ''')

    # Daily goals
    cur.execute('''
        CREATE TABLE IF NOT EXISTS daily_goals (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            goal_text TEXT,
            date DATE DEFAULT CURRENT_DATE,
            completed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Productivity metrics
    cur.execute('''
        CREATE TABLE IF NOT EXISTS productivity_metrics (
            user_id BIGINT,
            date DATE,
            tasks_completed INTEGER DEFAULT 0,
            focus_minutes INTEGER DEFAULT 0,
            distractions INTEGER DEFAULT 0,
            productivity_score INTEGER,
            PRIMARY KEY (user_id, date)
        )
    ''')

    conn.commit()
    cur.close()
    logger.info("✅ Productivity tables initialized")


# === TASK MANAGEMENT ===

def add_task(conn, user_id, title, description="", priority="medium", category="general", due_date=None, estimated_minutes=None):
    """Vazifa qo'shish"""
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO tasks (user_id, title, description, priority, category, due_date, estimated_minutes)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    ''', (user_id, title, description, priority, category, due_date, estimated_minutes))
    task_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    return task_id


def complete_task(conn, task_id):
    """Vazifani bajarish"""
    cur = conn.cursor()
    cur.execute('''
        UPDATE tasks SET completed = TRUE, completed_at = NOW()
        WHERE id = %s
        RETURNING user_id
    ''', (task_id,))
    result = cur.fetchone()
    conn.commit()
    cur.close()

    if result:
        user_id = result[0]
        # Update productivity metrics
        update_daily_metrics(conn, user_id, tasks_completed=1)
        return True
    return False


def get_user_tasks(conn, user_id, include_completed=False):
    """Foydalanuvchi vazifalari"""
    cur = conn.cursor()

    if include_completed:
        cur.execute('''
            SELECT id, title, priority, due_date, completed
            FROM tasks WHERE user_id = %s
            ORDER BY completed ASC, priority DESC, due_date ASC
            LIMIT 50
        ''', (user_id,))
    else:
        cur.execute('''
            SELECT id, title, priority, due_date, completed
            FROM tasks WHERE user_id = %s AND completed = FALSE
            ORDER BY priority DESC, due_date ASC
            LIMIT 20
        ''', (user_id,))

    tasks = []
    for row in cur.fetchall():
        tasks.append({
            "id": row[0],
            "title": row[1],
            "priority": row[2],
            "due_date": row[3],
            "completed": row[4]
        })

    cur.close()
    return tasks


def update_daily_metrics(conn, user_id, tasks_completed=0, focus_minutes=0, distractions=0):
    """Kunlik metrikalarni yangilash"""
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO productivity_metrics (user_id, date, tasks_completed, focus_minutes, distractions)
        VALUES (%s, CURRENT_DATE, %s, %s, %s)
        ON CONFLICT (user_id, date) DO UPDATE SET
            tasks_completed = productivity_metrics.tasks_completed + %s,
            focus_minutes = productivity_metrics.focus_minutes + %s,
            distractions = productivity_metrics.distractions + %s
    ''', (user_id, tasks_completed, focus_minutes, distractions, tasks_completed, focus_minutes, distractions))
    conn.commit()
    cur.close()


# === AI PRODUCTIVITY COACH ===

async def prioritize_tasks_ai(tasks, user_context=""):
    """AI orqali vazifalarni ustuvorlik bo'yicha tartiblash"""
    try:
        tasks_text = "\n".join([f"- {t['title']}" for t in tasks])

        prompt = f"""Quyidagi vazifalarni Eisenhower Matrix (muhim/shoshilinch) bo'yicha tartiblang:

Vazifalar:
{tasks_text}

Kontekst: {user_context}

Har bir vazifa uchun:
1. Ustuvorlik (urgent/high/medium/low)
2. Qisqa izoh (nega shunday?)
3. Tavsiya (qachon va qanday bajarish)

Javob JSON formatda:
```json
[
  {{"task": "vazifa nomi", "priority": "urgent", "reason": "sabab", "advice": "maslahat"}},
  ...
]
```"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.5
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Task prioritization error: {e}")
        return None


async def create_daily_plan(user_id, conn, work_hours=8, lang="uz"):
    """Kunlik reja yaratish"""
    try:
        tasks = get_user_tasks(conn, user_id, include_completed=False)

        if not tasks:
            return "📝 Hozircha vazifalar yo'q. /add_task buyrug'i bilan vazifa qo'shing."

        tasks_text = "\n".join([
            f"- {t['title']} (Ustuvorlik: {t['priority']})"
            for t in tasks
        ])

        prompt = f"""Bugun uchun optimal kunlik reja yarating.

Ish vaqti: {work_hours} soat

Vazifalar:
{tasks_text}

Pomodoro texnikasi (25 min ish + 5 min tanaffus) asosida reja tuzing.
Har bir vazifa uchun vaqt ajrating.
Kun davomida taqsimlang.

Format:
08:00-08:25 - Vazifa 1
08:25-08:30 - Tanaffus
...

O'zbek tilida, emoji bilan."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.6
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Daily plan error: {e}")
        return "⚠️ Reja yaratishda xatolik."


async def analyze_productivity(user_id, conn, days=7, lang="uz"):
    """Unumdorlikni tahlil qilish"""
    try:
        cur = conn.cursor()

        # Get productivity data for last N days
        cur.execute('''
            SELECT date, tasks_completed, focus_minutes, distractions
            FROM productivity_metrics
            WHERE user_id = %s AND date >= CURRENT_DATE - INTERVAL '%s days'
            ORDER BY date DESC
        ''', (user_id, days))

        data = cur.fetchall()
        cur.close()

        if not data:
            return "📊 Hali ma'lumot yo'q. Vazifalarni bajaring va natijalarni ko'ring!"

        # Format data for AI
        stats_text = "\n".join([
            f"{row[0]}: {row[1]} vazifa, {row[2]} min fokus, {row[3]} chalg'itish"
            for row in data
        ])

        prompt = f"""So'nggi {days} kunlik unumdorlik tahlili:

{stats_text}

Quyidagilarni tahlil qiling:
1. Trend (o'sib/kamayibmi?)
2. Eng produktiv kunlar
3. Muammolar (agar bor bo'lsa)
4. 3 ta aniq tavsiya yaxshilash uchun
5. Maqsad (keyingi hafta uchun)

O'zbek tilida, emoji va grafiklar bilan."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.6
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Productivity analysis error: {e}")
        return "⚠️ Tahlil qilishda xatolik."


# === POMODORO TIMER ===

def start_focus_session(conn, user_id, task_id=None, duration=25):
    """Fokus sessiyasini boshlash"""
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO focus_sessions (user_id, task_id, duration_minutes)
        VALUES (%s, %s, %s)
        RETURNING id
    ''', (user_id, task_id, duration))
    session_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    return session_id


def complete_focus_session(conn, session_id):
    """Fokus sessiyasini yakunlash"""
    cur = conn.cursor()
    cur.execute('''
        UPDATE focus_sessions SET completed = TRUE
        WHERE id = %s
        RETURNING user_id, duration_minutes
    ''', (session_id,))
    result = cur.fetchone()
    conn.commit()
    cur.close()

    if result:
        user_id, duration = result
        # Update metrics
        update_daily_metrics(conn, user_id, focus_minutes=duration)
        return True
    return False


# === TIME BLOCKING ===

async def create_time_blocks(events, available_hours=8):
    """Time blocking - vaqtni bloklash"""
    try:
        events_text = "\n".join([f"- {e}" for e in events])

        prompt = f"""Time blocking texnikasi bilan kun rejasi yarating.

Mavjud vaqt: {available_hours} soat

Vazifalar/uchrashuvlar:
{events_text}

Deep work (chuqur ish) uchun 2-3 soatlik bloklar ajrating.
Hozirgi kun uchun optimal jadval tuzing.

Format:
08:00-10:00 🔴 Deep Work: Muhim vazifa
10:00-10:15 ☕ Tanaffus
...

O'zbek tilida."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.6
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Time blocking error: {e}")
        return "⚠️ Jadval yaratishda xatolik."


# === DISTRACTION MANAGEMENT ===

async def analyze_distractions(user_id, conn):
    """Chalg'itishlarni tahlil qilish"""
    cur = conn.cursor()

    # Get recent distraction count
    cur.execute('''
        SELECT SUM(distractions) FROM productivity_metrics
        WHERE user_id = %s AND date >= CURRENT_DATE - INTERVAL '7 days'
    ''', (user_id,))

    total = cur.fetchone()[0] or 0
    cur.close()

    if total == 0:
        return "✅ Ajoyib! Haftada chalg'itishlar bo'lmagan."

    prompt = f"""Foydalanuvchi so'nggi haftada {total} marta chalg'itilgan.

Quyidagilarni taklif qiling:
1. Umumiy chalg'itishlar (ijtimoiy tarmoq, telefon, etc.)
2. Har biri uchun yechim
3. Fokusni oshirish texnikalari
4. App/vositalar (blokerlar, timer)
5. Environment sozlash (ish joyi)

O'zbek tilida, amaliy maslahatlar."""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=700,
            temperature=0.7
        )
        return response.choices[0].message.content
    except:
        return "⚠️ Tahlil qilishda xatolik."


# === LANGUAGE TEXTS ===

def get_productivity_texts(lang="uz"):
    """Productivity matnlar"""
    return {
        "uz": {
            "menu": """⚡ **Productivity Coach**

Nima yordam kerak?""",
            "add_task_prompt": "📝 Vazifa nomini kiriting:",
            "task_added": "✅ Vazifa qo'shildi: {title}",
            "task_completed": "🎉 Vazifa bajarildi! Tabriklaymiz!",
            "no_tasks": "📝 Hozircha vazifalar yo'q.",
            "focus_start": "🎯 Fokus sessiyasi boshlandi!\n⏱️ {duration} minut\n\n💡 Telefon va ijtimoiy tarmoqlarni yoping.",
            "focus_end": "🎉 Fokus sessiyasi tugadi!\n\n☕ 5 daqiqa dam oling.",
            "daily_plan": "📅 **Bugungi Reja**\n\n{plan}",
            "productivity_report": "📊 **Unumdorlik Hisoboti**\n\n{report}"
        }
    }.get(lang, {})
