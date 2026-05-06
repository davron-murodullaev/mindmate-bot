"""
English translations
"""

TRANSLATIONS = {
    "welcome": "👋 Welcome to MindMate!\n\nI'm your AI-powered companion for mental health and productivity.\n\nPlease select your language:",

    "setup": {
        "complete": "✅ Setup complete! You can now use all features.",
        "choose_timezone": "Please choose your timezone:",
    },

    "menu": {
        "main_menu": "🏠 Main Menu\n\nWhat would you like to do today?",
        "mood_tracking": "😊 Mood",
        "healer": "🌟 Healer",
        "journal": "📝 Journal",
        "productivity": "🎯 Productivity",
        "reminders": "⏰ Reminders",
        "stats": "📊 Statistics",
        "settings": "⚙️ Settings",
        "premium": "💎 Premium",
        "help": "❓ Help",
    },

    "mood": {
        "select": "How are you feeling today?",
        "logged": "✅ Mood logged successfully!",
        "happy": "Happy",
        "sad": "Sad",
        "angry": "Angry",
        "anxious": "Anxious",
        "tired": "Tired",
        "excited": "Excited",
        "stats": "📊 Your mood statistics for the past {days} days:",
        "no_data": "No mood data yet. Log your first mood!",
    },

    "healer": {
        "welcome": "🌟 Welcome to Healer Mode\n\nI'm here to listen and provide support. Feel free to share what's on your mind.\n\nType your message below:",
        "active": "🌟 Healer Mode Active\n\nI'm listening. Share your thoughts and feelings:",
        "exit": "Thank you for sharing. Take care of yourself! 💚",
        "crisis": "Your life matters. Please reach out to professional help immediately:\n\n🆘 Crisis Hotlines:\n• 988 (US Suicide & Crisis Lifeline)\n• Text HOME to 741741\n• findahelpline.com (international)\n\nYou are not alone. 💚",
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

    "stats": {
        "welcome": "📊 Your Statistics\n\nWhat would you like to see?",
        "mood": "😊 Mood Stats",
        "journal": "📝 Journal Stats",
        "overall": "📈 Overall Stats",
        "summary": "📊 Overall stats ({days} days):\n\n• Mood entries: {moods}\n• Journal entries: {journals}\n• AI conversations: {chats}",
    },

    "reminders": {
        "welcome": "⏰ Reminders\n\nWhat would you like to do?",
        "new": "➕ New reminder",
        "list": "📋 My reminders",
        "set": "⏰ Set Reminder\n\nTell me when you'd like to be reminded and what for.\n\nExample: Remind me to drink water at 3pm tomorrow",
        "created": "✅ Reminder created!\n\nI'll remind you: {text}\nAt: {time}",
        "notification": "⏰ Reminder: {text}",
        "no_reminders": "You have no active reminders.",
        "list_item": "• {time} — {text}",
        "limit_reached": "❌ Free tier allows {limit} reminders max. Upgrade to Premium!",
        "parse_error": "❌ I couldn't understand the time. Please try again.\n\nExample: Tomorrow at 3pm meeting",
    },

    "settings": {
        "welcome": "⚙️ Settings",
        "language": "🌐 Language",
        "timezone": "🕐 Timezone",
        "delete_data": "🗑 Delete my data",
        "delete_confirm": "⚠️ All your data will be deleted. Continue?",
        "delete_done": "✅ Your data has been deleted.",
    },

    "premium": {
        "welcome": "💎 Premium Subscription\n\nPremium benefits:\n\n✅ Unlimited AI conversations\n✅ Unlimited reminders\n✅ Deep statistics\n✅ Voice messages\n✅ Priority response\n\nPrice: $2.99/month",
        "subscribe_stars": "⭐ Pay with Telegram Stars (200⭐)",
        "subscribe_card": "💳 Pay with Card",
        "active": "✅ Premium active until: {date}",
        "limit_reached": "❌ Daily free limit reached ({limit} messages). Upgrade to Premium!",
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
