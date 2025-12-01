# 🚀 MindMate - Quick Start Guide

Get your MindMate bot up and running in 5 minutes!

---

## ⚡ Quick Setup (Local Development)

### 1️⃣ Prerequisites Check
```bash
# Check Python version (need 3.8+)
python --version

# Check PostgreSQL (need 13+)
psql --version
```

### 2️⃣ Clone & Install
```bash
# Clone repository
git clone https://github.com/yourusername/mindmate-bot.git
cd mindmate-bot

# Install dependencies
pip install -r requirements.txt
```

### 3️⃣ Get API Keys

**Telegram Bot Token:**
1. Open [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot`
3. Follow instructions
4. Copy your bot token

**OpenAI API Key:**
1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up/Login
3. Go to API Keys section
4. Create new key
5. Copy the key

### 4️⃣ Configure Environment
```bash
# Copy example file
cp .env.example .env

# Edit .env file with your favorite editor
nano .env  # or notepad .env on Windows
```

**Add your credentials:**
```env
TELEGRAM_BOT_TOKEN=your_telegram_token_here
OPENAI_API_KEY=your_openai_key_here
DATABASE_URL=postgresql://postgres:password@localhost:5432/mindmate
```

### 5️⃣ Setup Database
```bash
# Create database
createdb mindmate

# Or using psql
psql -U postgres
CREATE DATABASE mindmate;
\q
```

### 6️⃣ Run Tests (Optional but Recommended)
```bash
python test_bot.py
```

Expected output:
```
✅ All imports successful
✅ Language system working (13 languages)
✅ AI prompts working
✅ Fitness module working
✅ Healer module working
✅ Reminder system working
✅ All environment variables set
📊 Test Results: 7 passed, 0 failed
✅ All tests passed! Bot is ready to run.
```

### 7️⃣ Start the Bot
```bash
python main.py
```

You should see:
```
✅ Database initialized with reminders system and indexes
✅ Reminder scheduler started
✅ MindMate JARVIS bot ishga tushdi!
```

### 8️⃣ Test on Telegram
1. Open Telegram
2. Search for your bot by username
3. Send `/start`
4. Enjoy! 🎉

---

## 🐳 Quick Setup (Docker)

### 1️⃣ Install Docker
- Windows/Mac: [Docker Desktop](https://www.docker.com/products/docker-desktop)
- Linux: `curl -fsSL https://get.docker.com | sh`

### 2️⃣ Clone Repository
```bash
git clone https://github.com/yourusername/mindmate-bot.git
cd mindmate-bot
```

### 3️⃣ Configure
Edit `docker-compose.yml` and add your tokens:
```yaml
environment:
  TELEGRAM_BOT_TOKEN: your_token_here
  OPENAI_API_KEY: your_key_here
```

### 4️⃣ Run
```bash
docker-compose up -d
```

### 5️⃣ Check Logs
```bash
docker-compose logs -f bot
```

### 6️⃣ Stop
```bash
docker-compose down
```

---

## ☁️ Quick Deploy to Cloud

### Heroku (Free Tier Available)
```bash
# Install Heroku CLI
# Then:
heroku login
heroku create your-bot-name
heroku addons:create heroku-postgresql:mini
heroku config:set TELEGRAM_BOT_TOKEN=your_token
heroku config:set OPENAI_API_KEY=your_key
git push heroku main
heroku ps:scale worker=1
```

### Render (Free Tier Available)
1. Go to [render.com](https://render.com)
2. Create PostgreSQL database
3. Create Background Worker
4. Connect GitHub repo
5. Add environment variables
6. Deploy!

---

## 🧪 Testing Checklist

Once your bot is running, test these features:

- [ ] `/start` - Bot responds with welcome message
- [ ] `/help` - Shows all features
- [ ] `/mood` - Mood tracking works
- [ ] `/journal` - Can write journal entry
- [ ] `/meditate` - Shows meditation options
- [ ] `/fitness` - Shows workout routines
- [ ] `/healer` - Natural healer mode works
- [ ] `/reminders` - Can set reminders
- [ ] `/stats` - Shows statistics
- [ ] `/lang` - Language switching works
- [ ] Regular chat - AI responds correctly

---

## ❓ Troubleshooting

### Bot doesn't start
```bash
# Check environment variables
cat .env  # or type .env on Windows

# Check database connection
psql $DATABASE_URL

# Check Python version
python --version  # Must be 3.8+
```

### Database errors
```bash
# Recreate database
dropdb mindmate
createdb mindmate
python main.py  # Auto-creates tables
```

### Import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### OpenAI errors
- Check API key is valid
- Verify you have credits
- Check rate limits

### Telegram errors
- Verify bot token is correct
- Check bot is not blocked
- Ensure internet connection

---

## 📚 Next Steps

Now that your bot is running:

1. **Read Full Documentation**
   - [README.md](README.md) - Complete guide
   - [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment

2. **Customize**
   - Edit prompts in `ai_brain.py`
   - Add translations in `languages.py`
   - Modify features as needed

3. **Monitor**
   - Check logs regularly
   - Monitor OpenAI usage
   - Backup database

4. **Contribute**
   - Report bugs
   - Suggest features
   - Submit pull requests

---

## 🆘 Need Help?

- **Documentation**: Check [README.md](README.md)
- **Issues**: [GitHub Issues](https://github.com/yourusername/mindmate-bot/issues)
- **Email**: your.email@example.com

---

## 🎉 Success!

Your MindMate bot is now running! Start chatting and enjoy your personal AI wellness assistant.

**Pro Tips:**
- Use `/lang` to change language
- Set daily reminders for best results
- Journal regularly for better AI insights
- Check `/stats` to track progress

---

**Happy Wellness! 🧠💚**
