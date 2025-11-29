# MindMate Bot - Developer Guide

VS Code'da ishlatish uchun to'liq yo'riqnoma.

## 📁 Loyiha Tuzilishi

```
MindMate/
├── main.py              # Asosiy bot logikasi (1000+ lines)
├── ai_brain.py          # AI promptlar va xotira tizimi
├── motivation.py        # Motivatsion xabarlar va kunlik ilhom
├── languages.py         # 3 til: O'zbek, Rus, Ingliz
├── fitness.py           # Fitness mashqlari
├── healer.py            # Tabiiy shifokorlik
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── .gitignore          # Git ignore fayllari
├── README.md           # Asosiy dokumentatsiya
├── TELEGRAM_SETUP.md   # Telegram bot sozlamalari
└── DEV_GUIDE.md        # Bu fayl
```

---

## 🚀 Tez Boshlanish (VS Code)

### 1. Terminal ochish

VS Code'da: `Ctrl + `` (backtick)

### 2. Virtual environment yaratish

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### 3. Dependencies o'rnatish

```bash
pip install -r requirements.txt
```

### 4. .env fayl yaratish

```bash
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac
```

`.env` faylini VS Code'da oching va to'ldiring:

```env
TELEGRAM_BOT_TOKEN=your_bot_token
OPENAI_API_KEY=your_openai_key
DATABASE_URL=your_postgresql_url
```

### 5. Botni ishga tushirish

```bash
python main.py
```

---

## 🛠️ VS Code Extensions (Tavsiya)

1. **Python** (Microsoft) - Python uchun asosiy extension
2. **Pylance** - Python IntelliSense
3. **GitLens** - Git visualization
4. **Error Lens** - Xatolarni inline ko'rsatish
5. **Better Comments** - Rangli kommentariyalar
6. **autoDocstring** - Docstring generator

---

## 📝 Yangi Funksiya Qo'shish

### 1. Yangi Command qo'shish

`main.py` faylida:

```python
# 1. Command handler funksiyasi yaratish
async def new_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    # Sizning kodingiz
    await update.message.reply_text("Xabar", parse_mode="Markdown")

# 2. main() funksiyasida handleni qo'shish
app.add_handler(CommandHandler("new_command", new_command))
```

### 2. Yangi Callback qo'shish

`button_callback` funksiyasida:

```python
# Yangi callback data
if query.data == "new_action":
    # Sizning kodingiz
    await safe_edit(query, "Xabar", reply_markup=get_back_button(lang))
    return
```

### 3. Yangi Database jadvali

`init_db()` funksiyasida:

```python
cur.execute('''
    CREATE TABLE IF NOT EXISTS new_table (
        id SERIAL PRIMARY KEY,
        user_id BIGINT,
        data TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
```

---

## 🔍 Debugging

### VS Code'da Debug sozlash

`.vscode/launch.json` yarating:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: MindMate Bot",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/main.py",
            "console": "integratedTerminal",
            "justMyCode": true,
            "envFile": "${workspaceFolder}/.env"
        }
    ]
}
```

Keyin `F5` bosib debug mode'ni ishga tushiring.

### Breakpoint qo'yish

1. VS Code'da kerakli qatorning chap tomoniga bosing (qizil nuqta paydo bo'ladi)
2. `F5` bosib debug'ni boshlang
3. Kod breakpoint'ga yetganda to'xtaydi

---

## 📊 Database

### PostgreSQL'ga ulanish

VS Code'da PostgreSQL extension o'rnating va database'ga ulaning:

```
Host: your_host
Port: 5432
Database: your_db_name
Username: your_username
Password: your_password
```

### Query'larni test qilish

`psql` yoki `pgAdmin` ishlatib query'larni test qiling:

```sql
-- Barcha userlarni ko'rish
SELECT * FROM users LIMIT 10;

-- User xotiralarini ko'rish
SELECT * FROM user_memories WHERE user_id = 123456789;

-- Statistika
SELECT
    COUNT(DISTINCT user_id) as total_users,
    COUNT(*) as total_moods
FROM moods;
```

---

## 🎨 Kod Style

### Python PEP 8

```python
# Yaxshi
def get_user_data(user_id: int) -> dict:
    """Foydalanuvchi ma'lumotlarini olish"""
    return {"id": user_id}

# Yomon
def getUserData(userId):
    return {"id":userId}
```

### Docstrings

```python
def calculate_mood_average(user_id: int, days: int = 7) -> float:
    """
    Foydalanuvchining o'rtacha kayfiyatini hisoblash

    Args:
        user_id (int): Foydalanuvchi ID
        days (int): Necha kunlik ma'lumot (default: 7)

    Returns:
        float: O'rtacha kayfiyat (0-5)
    """
    pass
```

---

## 🧪 Testing

### Manual test

Terminal'da:

```bash
python main.py
```

Telegram'da botni test qiling:
- `/start` - Bosh menyu
- Barcha tugmalarni bosib ko'ring
- Xabar yuboring

### Error handling test

Xato holatlarni test qiling:
- Internet yo'q
- Database ulanmadi
- API key noto'g'ri

---

## 📤 Git Workflow

### 1. O'zgarishlarni ko'rish

```bash
git status
git diff
```

### 2. Commit qilish

```bash
git add main.py motivation.py
git commit -m "Add new feature: daily motivation"
```

### 3. Push qilish

```bash
git push origin keen-germain
```

### 4. Pull request

GitHub'da pull request ochish.

---

## 🚀 Deploy (Render.com)

### 1. GitHub'ga push

```bash
git push origin keen-germain
```

### 2. Render'da deploy

Render avtomatik deploy qiladi. Logs'ni kuzating:

- render.com → Service → Logs
- "Deploy successful" ni kutish

### 3. Xatolarni ko'rish

```bash
# Render logs
render.com → Service → Logs → Filter: ERROR
```

---

## 🔧 Troubleshooting

### Problem: Bot javob bermayapti

**Yechim:**
1. Logs'ni tekshiring
2. DATABASE_URL to'g'rimi?
3. TELEGRAM_TOKEN to'g'rimi?

### Problem: Markdown xatosi

**Yechim:**
```python
# escape_markdown() funksiyadan foydalaning
safe_text = escape_markdown(user_input)
await update.message.reply_text(safe_text, parse_mode="Markdown")
```

### Problem: Database connection error

**Yechim:**
```python
# get_db() funksiyasi None qaytarsa
conn = get_db()
if conn is None:
    logger.error("Database connection failed!")
    return
```

---

## 📚 Foydali Linklar

- [python-telegram-bot docs](https://docs.python-telegram-bot.org/)
- [OpenAI API docs](https://platform.openai.com/docs)
- [PostgreSQL docs](https://www.postgresql.org/docs/)
- [Render docs](https://render.com/docs)

---

## 🎯 Keyingi Qadamlar

1. [ ] Voice message qo'llab-quvvatlash
2. [ ] Rasm yuklash va tahlil
3. [ ] Eslatmalar tizimi
4. [ ] Haftalik hisobotlar
5. [ ] Premium funksiyalar

---

## 💡 Pro Tips

1. **VS Code Shortcuts:**
   - `Ctrl + P` - Tez fayl ochish
   - `Ctrl + Shift + F` - Barcha faylda qidirish
   - `Ctrl + D` - Bir xil so'zlarni tanlash
   - `Alt + Up/Down` - Qatorni ko'chirish
   - `Ctrl + /` - Komment qilish

2. **Python Debugging:**
   ```python
   # Tez debug
   print(f"DEBUG: user_id={user_id}, lang={lang}")

   # Logger ishlatish (yaxshiroq)
   logger.info(f"User {user_id} started bot")
   logger.error(f"Error: {e}")
   ```

3. **Database Query Optimization:**
   ```python
   # Yomon - har safar ulanish
   for user_id in user_ids:
       conn = get_db()
       # query
       conn.close()

   # Yaxshi - bir marta ulanish
   conn = get_db()
   for user_id in user_ids:
       # query
   conn.close()
   ```

---

Muvaffaqiyatlar! 🚀
