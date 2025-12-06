"""
English translations
"""

TRANSLATIONS = {
    "welcome": "👋 Welcome to MindMate!\n\nI'm your AI-powered companion for mental health, productivity, and wellness.\n\nPlease select your language:",

    "setup": {
        "complete": "✅ Setup complete! You can now use all features.",
        "choose_timezone": "Please choose your timezone:",
    },

    "menu": {
        "main_menu": "🏠 Main Menu\n\nWhat would you like to do today?",
        "mood_tracking": "😊 Mood Tracking",
        "meditation": "🧘 Meditation",
        "fitness": "💪 Fitness",
        "healer": "🌟 Talk to Healer",
        "journal": "📝 Journal",
        "productivity": "🎯 Productivity",
        "finance": "💰 Finance",
        "stats": "📊 Statistics",
        "settings": "⚙️ Settings",
        "help": "❓ Help",
    },

    "mood": {
        "select": "How are you feeling today?",
        "logged": "✅ Mood logged successfully!",
        "happy": "😊 Happy",
        "sad": "😢 Sad",
        "angry": "😠 Angry",
        "anxious": "😰 Anxious",
        "tired": "😴 Tired",
        "excited": "🤗 Excited",
        "stats": "📊 Your mood statistics for the past {days} days:",
    },

    "meditation": {
        "welcome": "🧘 Welcome to Meditation\n\nSelect your meditation duration:",
        "duration_5": "5 minutes",
        "duration_10": "10 minutes",
        "duration_15": "15 minutes",
        "duration_20": "20 minutes",
        "duration_30": "30 minutes",
        "start": "🧘 Starting {duration} minute meditation session...\n\nFind a comfortable position, close your eyes, and focus on your breath.\n\nI'll notify you when the session is complete.",
        "complete": "✅ Meditation session complete!\n\nGreat job! You've completed a {duration} minute meditation session.",
        "stats": "📊 Meditation Statistics:\n\nTotal sessions: {total}\nTotal time: {time} minutes\nAverage duration: {avg} minutes",
    },

    "fitness": {
        "welcome": "💪 Fitness Tracking\n\nWhat would you like to do?",
        "log_workout": "📝 Log Workout",
        "view_stats": "📊 View Statistics",
        "enter_workout": "Please enter your workout details in this format:\n\nActivity: duration (minutes)\n\nExample: Running: 30",
        "logged": "✅ Workout logged successfully!\n\nActivity: {activity}\nDuration: {duration} minutes",
        "stats": "📊 Fitness Statistics (Past {days} days):\n\nTotal workouts: {total}\nTotal duration: {duration} minutes\nAverage duration: {avg} minutes",
    },

    "healer": {
        "welcome": "🌟 Welcome to Healer Mode\n\nI'm here to listen and provide support. Feel free to share what's on your mind.\n\nType your message below:",
        "active": "🌟 Healer Mode Active\n\nI'm listening. Share your thoughts and feelings:",
        "exit": "Thank you for sharing. Take care of yourself! 💚",
    },

    "journal": {
        "welcome": "📝 Journal\n\nWhat would you like to do?",
        "new_entry": "✍️ New Entry",
        "view_entries": "📖 View Entries",
        "enter_text": "Write your journal entry:\n\n(You can write as much as you'd like)",
        "saved": "✅ Journal entry saved!",
        "no_entries": "You don't have any journal entries yet.",
        "entry": "📝 Entry from {date}:\n\n{content}",
    },

    "productivity": {
        "welcome": "🎯 Productivity Coach\n\nI'm here to help you achieve your goals and boost your productivity!\n\nHow can I help you today?",
        "active": "🎯 Productivity Mode Active\n\nShare your tasks, goals, or ask for productivity advice:",
    },

    "finance": {
        "welcome": "💰 Finance Tracking\n\nWhat would you like to do?",
        "add_expense": "➕ Add Expense",
        "view_stats": "📊 View Statistics",
        "enter_expense": "Enter expense details in this format:\n\nAmount Category: Description\n\nExample: 50 food: Lunch at restaurant",
        "added": "✅ Expense added!\n\nAmount: ${amount}\nCategory: {category}",
        "stats": "📊 Finance Statistics (Past {days} days):\n\nTotal expenses: ${total}\nAverage expense: ${avg}\nNumber of transactions: {count}",
        "by_category": "💰 Expenses by Category:\n\n{categories}",
    },

    "stats": {
        "welcome": "📊 Your Statistics\n\nWhat would you like to see?",
        "mood": "😊 Mood Stats",
        "fitness": "💪 Fitness Stats",
        "meditation": "🧘 Meditation Stats",
        "finance": "💰 Finance Stats",
        "overall": "📈 Overall Stats",
    },

    "reminders": {
        "set": "⏰ Set Reminder\n\nTell me when you'd like to be reminded and what for.\n\nExample: Remind me to drink water at 3pm tomorrow",
        "created": "✅ Reminder created!\n\nI'll remind you: {text}\nAt: {time}",
        "notification": "⏰ Reminder: {text}",
    },

    "errors": {
        "generic": "❌ Something went wrong. Please try again.",
        "invalid_input": "❌ Invalid input. Please try again.",
        "database": "❌ Database error. Please contact support.",
        "ai_error": "❌ AI service is temporarily unavailable.",
    },

    "buttons": {
        "back": "⬅️ Back",
        "cancel": "❌ Cancel",
        "confirm": "✅ Confirm",
        "next": "➡️ Next",
    },
}
