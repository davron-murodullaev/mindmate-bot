# 🚀 MindMate Deployment Guide

This guide will help you deploy MindMate to various hosting platforms.

---

## 📋 Prerequisites

Before deploying, make sure you have:
- ✅ Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- ✅ OpenAI API Key
- ✅ PostgreSQL database (can be hosted separately)

---

## 🐳 Docker Deployment (Recommended)

### Using Docker Compose

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/mindmate-bot.git
cd mindmate-bot
```

2. **Configure environment variables**

Edit `docker-compose.yml` and update:
- Database password
- Your Telegram Bot Token
- Your OpenAI API Key

Or create a `.env` file:
```env
TELEGRAM_BOT_TOKEN=your_token_here
OPENAI_API_KEY=your_key_here
```

3. **Start the services**
```bash
docker-compose up -d
```

4. **Check logs**
```bash
docker-compose logs -f bot
```

5. **Stop the services**
```bash
docker-compose down
```

### Using Docker only

```bash
# Build the image
docker build -t mindmate-bot .

# Run the container
docker run -d \
  --name mindmate \
  -e TELEGRAM_BOT_TOKEN=your_token \
  -e OPENAI_API_KEY=your_key \
  -e DATABASE_URL=your_database_url \
  mindmate-bot
```

---

## ☁️ Heroku Deployment

1. **Install Heroku CLI**
```bash
# macOS
brew install heroku/brew/heroku

# Windows
# Download from https://devcenter.heroku.com/articles/heroku-cli
```

2. **Login to Heroku**
```bash
heroku login
```

3. **Create Heroku app**
```bash
heroku create your-mindmate-bot
```

4. **Add PostgreSQL addon**
```bash
heroku addons:create heroku-postgresql:mini
```

5. **Set environment variables**
```bash
heroku config:set TELEGRAM_BOT_TOKEN=your_token
heroku config:set OPENAI_API_KEY=your_key
```

6. **Deploy**
```bash
git push heroku main
```

7. **Scale the worker**
```bash
heroku ps:scale worker=1
```

8. **View logs**
```bash
heroku logs --tail
```

---

## 🌐 Render Deployment

1. **Create a new account** at [render.com](https://render.com)

2. **Create PostgreSQL database**
   - Click "New +" → "PostgreSQL"
   - Choose free tier
   - Note the connection string

3. **Create Web Service**
   - Click "New +" → "Background Worker"
   - Connect your GitHub repository
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python main.py`

4. **Add Environment Variables**
   - `TELEGRAM_BOT_TOKEN` = your bot token
   - `OPENAI_API_KEY` = your OpenAI key
   - `DATABASE_URL` = your PostgreSQL connection string

5. **Deploy**
   - Click "Create Background Worker"
   - Wait for deployment to complete

---

## 💻 VPS Deployment (Ubuntu/Debian)

1. **Update system**
```bash
sudo apt update && sudo apt upgrade -y
```

2. **Install dependencies**
```bash
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib
```

3. **Set up PostgreSQL**
```bash
sudo -u postgres psql
CREATE DATABASE mindmate;
CREATE USER mindmate_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE mindmate TO mindmate_user;
\q
```

4. **Clone repository**
```bash
cd /opt
sudo git clone https://github.com/yourusername/mindmate-bot.git
cd mindmate-bot
```

5. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

6. **Configure environment**
```bash
sudo nano .env
# Add your credentials
```

7. **Create systemd service**
```bash
sudo nano /etc/systemd/system/mindmate.service
```

Add:
```ini
[Unit]
Description=MindMate Telegram Bot
After=network.target postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/mindmate-bot
Environment="PATH=/opt/mindmate-bot/venv/bin"
ExecStart=/opt/mindmate-bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

8. **Start service**
```bash
sudo systemctl daemon-reload
sudo systemctl enable mindmate
sudo systemctl start mindmate
```

9. **Check status**
```bash
sudo systemctl status mindmate
sudo journalctl -u mindmate -f
```

---

## 🔧 Railway Deployment

1. **Create account** at [railway.app](https://railway.app)

2. **Install Railway CLI**
```bash
npm i -g @railway/cli
```

3. **Login**
```bash
railway login
```

4. **Initialize project**
```bash
railway init
```

5. **Add PostgreSQL**
```bash
railway add postgresql
```

6. **Set variables**
```bash
railway variables set TELEGRAM_BOT_TOKEN=your_token
railway variables set OPENAI_API_KEY=your_key
```

7. **Deploy**
```bash
railway up
```

---

## 📊 Monitoring & Maintenance

### Check Bot Status
```bash
# Docker
docker logs mindmate-bot

# Systemd
sudo systemctl status mindmate
sudo journalctl -u mindmate -f

# Heroku
heroku logs --tail
```

### Database Backup (PostgreSQL)
```bash
# Local backup
pg_dump -U mindmate_user mindmate > backup.sql

# Restore
psql -U mindmate_user mindmate < backup.sql
```

### Update Bot
```bash
# Pull latest changes
git pull origin main

# Restart service
# Docker
docker-compose restart bot

# Systemd
sudo systemctl restart mindmate

# Heroku
git push heroku main
```

---

## 🛡️ Security Best Practices

1. **Environment Variables**
   - Never commit `.env` file
   - Use strong database passwords
   - Rotate API keys regularly

2. **Database Security**
   - Enable SSL connections
   - Use firewall rules
   - Regular backups

3. **Bot Security**
   - Monitor logs for suspicious activity
   - Implement rate limiting
   - Keep dependencies updated

4. **Server Security**
   - Enable firewall (ufw/iptables)
   - Use SSH keys instead of passwords
   - Keep system updated
   - Use fail2ban for SSH protection

---

## 🔍 Troubleshooting

### Bot not responding
- Check if bot token is correct
- Verify database connection
- Check logs for errors

### Database connection issues
- Verify DATABASE_URL format
- Check firewall rules
- Ensure PostgreSQL is running

### OpenAI API errors
- Check API key validity
- Verify account has credits
- Check rate limits

### Memory issues
- Monitor bot memory usage
- Clear old conversation data
- Optimize database queries

---

## 📞 Support

For deployment issues:
- Check logs first
- Review this guide
- Open an issue on GitHub
- Contact: your.email@example.com

---

**Happy Deploying! 🚀**
