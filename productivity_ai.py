"""
Productivity & Time Management AI
Time management, tasks, focus, productivity
"""

import logging
from datetime import datetime, timedelta
from openai import OpenAI
import os

logger = logging.getLogger(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === TASK PRIORITIES ===

PRIORITY_LEVELS = {
    "urgent": {"name": "🔴 Urgent", "value": 4},
    "high": {"name": "🟠 High", "value": 3},
    "medium": {"name": "🟡 Medium", "value": 2},
    "low": {"name": "🟢 Low", "value": 1}
}

# === DATABASE ===

def init_productivity_tables(conn):
    """Productivity tables"""
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
    """Add task"""
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
    """Complete task"""
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
    """User tasks"""
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
    """Update daily metrics"""
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
    """Prioritize tasks using AI"""
    try:
        tasks_text = "\n".join([f"- {t['title']}" for t in tasks])

        prompt = f"""Prioritize the following tasks using the Eisenhower Matrix (important/urgent):

Tasks:
{tasks_text}

Context: {user_context}

For each task provide:
1. Priority (urgent/high/medium/low)
2. Brief explanation (why?)
3. Recommendation (when and how to complete)

Answer in JSON format:
```json
[
  {{"task": "task name", "priority": "urgent", "reason": "reason", "advice": "recommendation"}},
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


async def create_daily_plan(user_id, conn, work_hours=8, lang="en"):
    """Create daily plan"""
    try:
        tasks = get_user_tasks(conn, user_id, include_completed=False)

        if not tasks:
            return "📝 No tasks yet. Add a task with /add_task command."

        tasks_text = "\n".join([
            f"- {t['title']} (Priority: {t['priority']})"
            for t in tasks
        ])

        prompt = f"""Create an optimal daily plan for today.

Work hours: {work_hours} hours

Tasks:
{tasks_text}

Create a plan based on Pomodoro technique (25 min work + 5 min break).
Allocate time for each task.
Distribute throughout the day.

Format:
08:00-08:25 - Task 1
08:25-08:30 - Break
...

Use emojis."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.6
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Daily plan error: {e}")
        return "⚠️ Error creating plan."


async def analyze_productivity(user_id, conn, days=7, lang="en"):
    """Analyze productivity"""
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
            return "📊 No data yet. Complete tasks and see your results!"

        # Format data for AI
        stats_text = "\n".join([
            f"{row[0]}: {row[1]} tasks, {row[2]} min focus, {row[3]} distractions"
            for row in data
        ])

        prompt = f"""Productivity analysis for the last {days} days:

{stats_text}

Analyze the following:
1. Trend (increasing/decreasing?)
2. Most productive days
3. Problems (if any)
4. 3 specific recommendations for improvement
5. Goal (for next week)

Use emojis and charts."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.6
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Productivity analysis error: {e}")
        return "⚠️ Error analyzing productivity."


# === POMODORO TIMER ===

def start_focus_session(conn, user_id, task_id=None, duration=25):
    """Start focus session"""
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
    """Complete focus session"""
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
    """Time blocking"""
    try:
        events_text = "\n".join([f"- {e}" for e in events])

        prompt = f"""Create a daily schedule using time blocking technique.

Available time: {available_hours} hours

Tasks/meetings:
{events_text}

Allocate 2-3 hour blocks for deep work.
Create an optimal schedule for today.

Format:
08:00-10:00 🔴 Deep Work: Important task
10:00-10:15 ☕ Break
..."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.6
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Time blocking error: {e}")
        return "⚠️ Error creating schedule."


# === DISTRACTION MANAGEMENT ===

async def analyze_distractions(user_id, conn):
    """Analyze distractions"""
    cur = conn.cursor()

    # Get recent distraction count
    cur.execute('''
        SELECT SUM(distractions) FROM productivity_metrics
        WHERE user_id = %s AND date >= CURRENT_DATE - INTERVAL '7 days'
    ''', (user_id,))

    total = cur.fetchone()[0] or 0
    cur.close()

    if total == 0:
        return "✅ Excellent! No distractions this week."

    prompt = f"""The user has been distracted {total} times in the last week.

Recommend the following:
1. Common distractions (social media, phone, etc.)
2. Solutions for each
3. Techniques to increase focus
4. Apps/tools (blockers, timers)
5. Environment setup (workspace)

Provide practical advice."""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=700,
            temperature=0.7
        )
        return response.choices[0].message.content
    except:
        return "⚠️ Error analyzing distractions."


# === LANGUAGE TEXTS ===

def get_productivity_texts(lang="en"):
    """Productivity texts"""
    return {
        "en": {
            "menu": """⚡ **Productivity Coach**

How can I help you?""",
            "add_task_prompt": "📝 Enter task name:",
            "task_added": "✅ Task added: {title}",
            "task_completed": "🎉 Task completed! Congratulations!",
            "no_tasks": "📝 No tasks yet.",
            "focus_start": "🎯 Focus session started!\n⏱️ {duration} minutes\n\n💡 Close phone and social media.",
            "focus_end": "🎉 Focus session complete!\n\n☕ Take a 5 minute break.",
            "daily_plan": "📅 **Today's Plan**\n\n{plan}",
            "productivity_report": "📊 **Productivity Report**\n\n{report}"
        },
        "ru": {
            "menu": """⚡ **Productivity Coach**

Чем помочь?""",
            "add_task_prompt": "📝 Введи название задачи:",
            "task_added": "✅ Задача добавлена: {title}",
            "task_completed": "🎉 Задача выполнена! Поздравляю!",
            "no_tasks": "📝 Пока нет задач.",
            "focus_start": "🎯 Фокус-сессия началась!\n⏱️ {duration} минут\n\n💡 Закрой телефон и соцсети.",
            "focus_end": "🎉 Фокус-сессия завершена!\n\n☕ Отдохни 5 минут.",
            "daily_plan": "📅 **План на Сегодня**\n\n{plan}",
            "productivity_report": "📊 **Отчёт о Продуктивности**\n\n{report}"
        }
    }.get(lang, {})
