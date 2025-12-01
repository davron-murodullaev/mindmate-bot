# 🧠 MindMate - Your Personal JARVIS

**MindMate** is an intelligent Telegram bot that serves as your personal AI assistant for mental health, wellness, and lifestyle support. With JARVIS-level intelligence, MindMate remembers everything about you and provides personalized guidance.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)

---

## ✨ Features

### 🤖 AI-Powered Conversations
- **JARVIS-Level Intelligence**: Advanced memory system that remembers your preferences, problems, and personal details
- **Context-Aware Responses**: Uses conversation history and user memories for personalized interactions
- **Multi-Modal Support**: Handles complex conversations with emotional intelligence

### 🌍 Multi-Language Support (13 Languages)
- 🇺🇿 Uzbek (O'zbekcha)
- 🇷🇺 Russian (Русский)
- 🇬🇧 English
- 🇹🇷 Turkish (Türkçe)
- 🇸🇦 Arabic (العربية)
- 🇮🇳 Hindi (हिंदी)
- 🇨🇳 Chinese (中文)
- 🇰🇷 Korean (한국어)
- 🇯🇵 Japanese (日本語)
- 🇪🇸 Spanish (Español)
- 🇫🇷 French (Français)
- 🇩🇪 German (Deutsch)
- 🇵🇹 Portuguese (Português)

### 😊 Mental Health & Wellness
- **Mood Tracking**: Track your daily mood on a 5-point scale with AI analysis
- **Daily Journaling**: Write daily reflections with AI-powered insights
- **Meditation Guides**: Multiple meditation exercises (breathing, calm, sleep)
- **Natural Healer**: Get natural remedy suggestions and wellness advice
- **Fitness Routines**: Morning workouts, energy boosters, and relaxation exercises

### ⏰ Smart Reminders
- **Mood Check Reminders**: Regular prompts to log your mood
- **Meditation Reminders**: Stay consistent with your meditation practice
- **Workout Reminders**: Never skip your fitness routine
- **Water Intake Reminders**: Stay hydrated throughout the day

### 📊 Personal Statistics
- Comprehensive tracking of all activities
- Mood history and trends
- Workout and meditation progress
- Memory insights about what the AI knows about you

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- OpenAI API Key

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/mindmate-bot.git
cd mindmate-bot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql://username:password@localhost:5432/mindmate
```

4. **Set up PostgreSQL Database**

Create a new database:
```bash
createdb mindmate
```

The bot will automatically create all necessary tables and indexes on first run.

5. **Run the bot**
```bash
python main.py
```

---

## 📋 Available Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and see the main menu |
| `/help` | Get help and see all available features |
| `/mood` | Track your current mood |
| `/journal` | Write a journal entry |
| `/meditate` | Access meditation exercises |
| `/fitness` | Get workout routines |
| `/healer` | Consult the natural healer |
| `/reminders` | Set up daily reminders |
| `/stats` | View your personal statistics |
| `/reset` | Clear conversation history |
| `/lang` | Change interface language |

---

## 🏗️ Project Structure

```
MindMate/
├── main.py              # Main bot logic and handlers
├── ai_brain.py          # JARVIS AI prompts and personality
├── languages.py         # Multi-language translations (13 languages)
├── reminders.py         # Reminder system implementation
├── fitness.py           # Workout routines and exercises
├── healer.py            # Natural healer knowledge base
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not in git)
├── .env.example         # Example environment file
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

---

## 🗄️ Database Schema

The bot uses PostgreSQL with 8 tables:

1. **users** - User profiles and preferences
2. **moods** - Mood tracking history
3. **journals** - Daily journal entries
4. **conversations** - Chat history for context
5. **workouts** - Fitness activity tracking
6. **healer_sessions** - Natural healer consultations
7. **user_memories** - JARVIS-style memory system
8. **reminders** - Daily reminder schedules

All tables include proper indexes for optimal performance.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 🔒 Security & Privacy

- **Data Privacy**: All user data is stored securely in PostgreSQL
- **Secure Connections**: Uses SSL for database connections
- **API Security**: API keys are stored in environment variables
- **No Data Sharing**: Your conversations are private and never shared

**Important**: Keep your `.env` file secure and never commit it to version control!

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👨‍💻 Author

**Davron Murodullaev**

---

## 🙏 Acknowledgments

- OpenAI for GPT-3.5 API
- python-telegram-bot library
- PostgreSQL database
- All contributors and users

---

## 🐛 Bug Reports & Feature Requests

Found a bug or have a feature request? Please open an issue on GitHub:
[GitHub Issues](https://github.com/yourusername/mindmate-bot/issues)

---

## 📧 Contact

For questions or support, please contact: your.email@example.com

---

**Made with ❤️ for mental health and wellness**
