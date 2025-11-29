# MindMate - JARVIS darajasidagi Telegram Bot

Sizning shaxsiy AI yordamchingiz. Ruhiy qo'llab-quvvatlash, tabiiy shifokorlik, fitness va yana ko'p narsalar!

## Xususiyatlar

- 🧠 **JARVIS darajasidagi xotira** - Siz haqingizda hamma narsani eslab qoladi
- 💬 **Aqlli suhbat** - GPT-3.5 yordamida shaxsiylashtirilgan javoblar
- 🌿 **Tabiiy Shifokor** - Xalq tabobati va zamonaviy usullar
- 😊 **Kayfiyat kuzatuvi** - Har kungi kayfiyat tahlili
- 📝 **Kundalik** - Fikrlaringizni yozib boring
- 🧘 **Meditatsiya** - Tinchlanish va nafas mashqlari
- 💪 **Fitness** - Kun davomidagi mashqlar
- 🌍 **Ko'p tillilik** - O'zbek, Rus, Ingliz

## O'rnatish

### 1. Repositoryni klonlash

```bash
git clone https://github.com/your-username/mindmate-bot.git
cd mindmate-bot
```

### 2. Kerakli paketlarni o'rnatish

```bash
pip install -r requirements.txt
```

### 3. Environment Variables sozlash

`.env.example` faylini `.env` ga nusxalang:

```bash
cp .env.example .env
```

Keyin `.env` fayliga quyidagi ma'lumotlarni kiriting:

```env
# Telegram Bot Token (BotFather'dan oling)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# OpenAI API Key (platform.openai.com'dan oling)
OPENAI_API_KEY=your_openai_api_key_here

# PostgreSQL Database URL (Render yoki boshqa hosting)
DATABASE_URL=postgresql://user:password@host:port/database
```

### 4. Telegram Bot yaratish

1. Telegram'da [@BotFather](https://t.me/BotFather) botini toping
2. `/newbot` buyrug'ini yuboring
3. Bot uchun nom va username tanlang
4. BotFather sizga `TELEGRAM_BOT_TOKEN` beradi - uni `.env` fayliga qo'shing

### 5. OpenAI API Key olish

1. [platform.openai.com](https://platform.openai.com) ga kiring
2. Account → API Keys → Create new secret key
3. API keyni `.env` fayliga qo'shing

### 6. PostgreSQL Database (Render)

1. [render.com](https://render.com) ga kiring
2. New → PostgreSQL yarating
3. "Internal Database URL" ni `.env` fayliga qo'shing

### 7. Botni ishga tushirish

```bash
python main.py
```

## Loyiha tuzilishi

```
mindmate-bot/
├── main.py           # Asosiy bot logikasi
├── ai_brain.py       # AI promptlar va xotira tizimi
├── languages.py      # Ko'p tillilik
├── fitness.py        # Fitness mashqlari
├── healer.py         # Shifokorlik maslahatlari
├── requirements.txt  # Python paketlari
├── .env.example      # Environment variables namunasi
└── README.md         # Bu fayl
```

## Ishlatish

Bot ishga tushgandan so'ng, Telegram'da botingizni toping va `/start` buyrug'ini yuboring.

### Asosiy buyruqlar:

- `/start` - Bosh menyu
- `/help` - Yordam
- `/mood` - Kayfiyat belgilash
- `/journal` - Kundalik yozish
- `/meditate` - Meditatsiya
- `/fitness` - Mashqlar
- `/healer` - Tabiiy shifokor
- `/stats` - Statistikangiz
- `/lang` - Tilni o'zgartirish
- `/reset` - Suhbatni yangilash

## Render.com'ga deploy qilish

1. Render.com'da yangi "Web Service" yarating
2. GitHub repository'ingizni ulang
3. Environment Variables qo'shing:
   - `TELEGRAM_BOT_TOKEN`
   - `OPENAI_API_KEY`
   - `DATABASE_URL`
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `python main.py`

## Xavfsizlik

- `.env` faylini **hech qachon** git'ga qo'shmang
- API keylaringizni **hech kimga** bermang
- Production'da `DATABASE_URL`ni SSL bilan ishlating

## Litsenziya

MIT License

## Muallif

Sizning ismingiz

## Qo'llab-quvvatlash

Muammolar yoki savollar bo'lsa, GitHub Issues'da yozing.
