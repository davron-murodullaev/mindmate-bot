# MindMate Bot - ChatGPT/Claude uchun To'liq Context Prompt

Quyidagi matnni ChatGPT yoki boshqa AI assistant'ga copy/paste qiling:

---

## 📋 LOYIHA: MINDMATE TELEGRAM BOT

Men MindMate Telegram bot loyihasi ustida ishlayapman va sizning yordamingiz kerak.

### 🤖 Loyiha Haqida:
- **Nom:** MindMate Bot
- **Turi:** JARVIS-level AI assistant Telegram bot
- **Tillar:** Python 3.11+, python-telegram-bot v22+, PostgreSQL
- **Deploy:** Render.com
- **Qo'llab-quvvatlanadigan tillar:** English, Russian, Uzbek

### 🎯 Bot Funksiyalari:
1. **AI Friend** - Chat, Journal, Natural Healer
2. **Financial Coach** - Xarajat/daromad tracking, investitsiya maslahati
3. **Productivity** - Task management, focus sessions, daily plans
4. **Health** - Meditation, fitness, health AI
5. **Creative Tools** - PDF, PPT, image generation, code writing
6. **Premium System** - Subscription tiers (Free/Premium/Pro)
7. **Referral System** - Invite friends, earn bonuses

---

## 🔑 Muhim Ma'lumotlar:

### Credentials:
```
Bot Token: 8321854805:AAFdYxXdxplJ1PAWsgzlm6klnL7T-k6cjjs
Database: postgresql://mindmate_db_l6n0_user:9IjW2Qu8t1WeaQVoSPVvCrfdQP6fKEg1@dpg-d4kc472dbo4c73csoa10-a.oregon-postgres.render.com/mindmate_db_l6n0
PayPal: d.murodullaev@mail.ru
GitHub: davron-murodullaev/mindmate-bot
Branch: claude/fix-mindmate-shu-errors-01BGuhT5cSqjZ8V1yvCv66nd
```

### Repository Struktura:
```
/home/user/mindmate-bot/
├── main.py                    (2769 lines - asosiy bot logic)
├── premium.py                 (subscription & referrals)
├── financial_coach.py         (financial tracking)
├── productivity_ai.py         (task management)
├── ai_brain.py               (JARVIS AI prompts)
├── healer.py                 (natural healer mode)
├── fitness.py                (workout routines)
├── languages.py              (EN/RU/UZ translations)
├── enhanced_features.py      (menu functions)
├── .env                      (environment variables)
├── requirements.txt          (dependencies)
└── COMPLETE_PROJECT_SUMMARY.md (full documentation)
```

---

## ✅ OXIRGI BAJARILGAN ISHLAR:

### O'tgan Sessiyada (6 ta katta feature):
1. ✅ **Language System** - Til tizimi hamma joyda ishlaydi (EN/RU/UZ)
2. ✅ **Financial Amounts** - "50000" → "$50" format
3. ✅ **Investment Free Trial** - 3 bepul konsultatsiya/oy tracking
4. ✅ **PayPal Email** - d.murodullaev@mail.ru qo'shildi
5. ✅ **Support/Feedback** - Yangi feedback feature
6. ✅ **Referral Bonus** - 10 ta do'st = 7 kun premium (avtomatik)

### Oxirgi Sessiyada (3 ta kritik bug):
1. ✅ **Import Error Fixed** - `get_settings_menu` import xatosi tuzatildi
2. ✅ **.env Created** - Environment variables fayli yaratildi
3. ✅ **Variable Names Fixed** - TELEGRAM_BOT_TOKEN va BOT_TOKEN qo'shildi

### Oxirgi Commit:
```
Commit: 1f4fd9e
Message: 🔧 Fix critical bugs and add complete project documentation
Files: main.py, .env, COMPLETE_PROJECT_SUMMARY.md
```

---

## 🗄️ DATABASE STRUKTURA:

### Asosiy Jadvallar:
```sql
users (user_id, username, full_name, language, created_at)
subscriptions (user_id, tier, expires_at)
referrals (id, referrer_id, referred_id, created_at)
expenses (id, user_id, amount, category, description, date)
tasks (id, user_id, title, priority, completed)
usage_stats (id, user_id, feature, used_at)
feedback (id, user_id, feedback_text, created_at)
```

---

## 🚀 HOZIRGI HOLAT:

### ✅ Tayyor:
- Barcha kod syntax jihatdan to'g'ri
- Barcha kritik xatolar tuzatildi
- 6 ta katta feature bajarildi
- 3 ta bug tuzatildi
- To'liq dokumentatsiya yozildi

### ⏳ Qolgan Ishlar:
1. Render.com'da deploy qilish
2. Environment variables'ni tekshirish
3. Database migration o'tkazish (birinchi marta)
4. Botni test qilish

---

## 🐛 MA'LUM MUAMMOLAR:

### ⚠️ Critical - Migration Kerak:
Eski foydalanuvchilar `language='uz'` da, yangi default `'en'`.

**Yechim:**
```bash
psql $DATABASE_URL -c "UPDATE users SET language = 'en' WHERE language = 'uz';"
```

### ✅ Boshqa Muammolar:
Barcha muammolar hal qilindi!

---

## 📝 TO'LIQ DOKUMENTATSIYA:

Agar ko'proq ma'lumot kerak bo'lsa, quyidagi fayllarni o'qing:

1. **COMPLETE_PROJECT_SUMMARY.md** - To'liq ma'lumot (700+ lines)
   - Location: `/home/user/mindmate-bot/COMPLETE_PROJECT_SUMMARY.md`
   - Mavjud: Database schema, deployment guide, testing checklist

2. **SESSION_SUMMARY.md** - O'tgan sessiya ma'lumoti (421 lines)
   - Location: `/home/user/mindmate-bot/SESSION_SUMMARY.md`
   - Mavjud: Previous session context, all features

3. **MIGRATION_GUIDE.md** - Database migration yo'riqnomasi
   - Location: `/home/user/mindmate-bot/MIGRATION_GUIDE.md`
   - Mavjud: Migration commands, troubleshooting

---

## 🎯 MENING SAVOLIM / VAZIFAM:

[Bu yerga o'z savolingiz yoki vazifangizni yozing]

**Misol savollar:**
- "Botni Render.com'da qanday deploy qilaman?"
- "Database migration qanday o'tkaziladi?"
- "Yangi funksiya qo'shish kerak: [funksiya tavsifi]"
- "Bot ishlamayapti, xatoni qanday topaman?"
- "Telegram Stars to'lovini qanday test qilaman?"
- "Referral sistemasini qanday test qilaman?"
- "[Boshqa savol yoki vazifa]"

---

## 💡 QO'SHIMCHA CONTEXT:

### Subscription Tiers:
- **Free:** 10 AI/day, 3 PDF/month, 3 investment advice/month
- **Premium ($4.99/M):** 100 AI/day, 20 PDF/month, 20 investment/month
- **Pro ($14.99/M):** Unlimited everything

### Referral System:
- Har bir referral: +5 AI requests, +2 PDFs
- 10 referrals → +7 days Premium (avtomatik)
- 20 referrals → +7 days Premium (jami 14 days)

### Payment Methods:
- Telegram Stars (direct payment)
- PayPal (manual - d.murodullaev@mail.ru)

### Environment Variables:
```bash
TELEGRAM_BOT_TOKEN=8321854805:AAFdYxXdxplJ1PAWsgzlm6klnL7T-k6cjjs
DATABASE_URL=postgresql://...
OPENAI_API_KEY=sk-... (kerak bo'lsa qo'shing)
```

---

**Iltimos, yuqoridagi ma'lumotlarni hisobga olib mening savolim/vazifamga javob bering!**
