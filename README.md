# MindMate Bot 🤖

MindMate is an AI-powered Telegram bot designed to be your personal mental health companion, productivity assistant, and wellness guide.

## Features

- 🧠 **AI-Powered Conversations**: Multiple AI modes (Friend, Healer, Productivity Coach)
- 😊 **Mood Tracking**: Track and analyze your emotional well-being
- 🧘 **Meditation & Mindfulness**: Guided meditation sessions
- 💪 **Fitness Tracking**: Workout logging and fitness goals
- 📝 **Journaling**: Daily journaling with AI insights
- 💰 **Finance Tracking**: Expense tracking and budgeting
- 📊 **Statistics**: Comprehensive analytics on your wellness journey
- ⏰ **Smart Reminders**: Intelligent reminder system with natural language parsing
- 🌍 **Multi-language**: Support for English, Russian, and Uzbek

## Architecture

```
mindmate/
├── ai/                 # AI engines and routing logic
│   ├── engines/       # Specialized AI modes
│   ├── core.py        # Core AI functionality
│   ├── formatter.py   # Response formatting
│   ├── memory.py      # Conversation memory
│   └── routing.py     # Mode routing
├── core/              # Core configurations
├── db/                # Database layer
├── handlers/          # Telegram bot handlers
├── i18n/              # Internationalization
├── reminders/         # Reminder system
├── services/          # Business logic services
└── ui/                # User interface components
```

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Telegram Bot Token
- Anthropic API Key (for Claude AI)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/davron-murodullaev/mindmate-bot.git
cd mindmate-bot
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. Run the bot:
```bash
python main.py
```

## Environment Variables

```env
# Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
ADMIN_USER_IDS=123456789,987654321

# AI Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key
AI_MODEL=claude-3-5-sonnet-20241022

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/mindmate

# Optional
LOG_LEVEL=INFO
ENVIRONMENT=production
```

## Usage

Start a conversation with your bot on Telegram:
1. `/start` - Initialize the bot
2. Choose your language
3. Explore features through the main menu
4. Chat with AI in different modes
5. Track your wellness journey

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, email devsite554@gmail.com or open an issue on GitHub.
