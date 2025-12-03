# ===============================================
# RENDER.COM'DA DATABASE MIGRATION - TO'G'RI USUL
# ===============================================

## Usul 1: Render Dashboard'da "Connect" → psql command

1. **Render.com Dashboard** → **PostgreSQL database**ni tanlang
2. **"Connect"** tugmasini bosing
3. **"External Connection"** tab'ini oching
4. **"PSQL Command"**ni nusxalang (masalan):

```bash
PGPASSWORD=9IjW2... psql -h dpg-d4kc472dbo4c73csoa10-a.oregon-postgres.render.com -U mindmate_db_l6n0_user mindmate_db_l6n0
```

5. Shu buyruqni **Shell** (Render Dashboard'da) yoki **local terminal**da bajaring

## Usul 2: Python script bilan (Render Web Service Shell'da)

```bash
cd ~/project/src
python3 migrate_users_to_english.py
```

## Usul 3: Render Dashboard - SQL Query Editor

Ba'zi Render planlarida SQL Query Editor bo'ladi - shuni ishlating

---

## ⚠️ SIZNING XATO:

```bash
render@srv-...:~/project/src$ SELECT language, COUNT(*) FROM users GROUP BY language;
bash: syntax error near unexpected token `('
```

**Muammo:** Siz SQL'ni bash shell'da ishlatmoqchisiz, lekin bash SQL'ni tushunmaydi!

**To'g'ri:** psql client orqali yoki Python script orqali

---

## ✅ ENG OSON USUL - PYTHON SCRIPT:

Render Web Service Shell'da:

```bash
cd ~/project/src

# 1. psycopg2 o'rnatish
pip install psycopg2-binary

# 2. Migration scriptni ishga tushirish
python3 migrate_users_to_english.py
```

Bu script DATABASE_URL'ni .env yoki environment'dan o'qiydi va automatic migration qiladi.

---

## 📝 YOKI MANUAL PSQL:

Agar psql command bor bo'lsa:

```bash
# 1. psql'ga ulanish
PGPASSWORD=9IjW2Qu8t1WeaQVoSPVvCrfdQP6fKEg1 psql -h dpg-d4kc472dbo4c73csoa10-a.oregon-postgres.render.com -U mindmate_db_l6n0_user mindmate_db_l6n0

# 2. SQL ishga tushirish
SELECT language, COUNT(*) FROM users GROUP BY language;

UPDATE users SET language = 'en' WHERE language = 'uz';

SELECT language, COUNT(*) FROM users GROUP BY language;

# 3. Chiqish
\q
```

---

## 🎯 TAVSIYA:

**Python script eng oson!** Chunki:
- Environment variables avtomatik o'qiladi
- Xatoliklarni ko'rsatadi
- Migratsiya natijasini chiroyli formatda ko'rsatadi
