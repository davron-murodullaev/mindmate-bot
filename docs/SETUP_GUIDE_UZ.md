# 🚀 TradeMate Bot - 0dan To'liq O'rnatish Qo'llanmasi

**Davron uchun maxsus - hamma narsani batafsil tushuntiraman! 💪**

---

## 📋 MUNDARIJA

1. [Kerakli Narsalar](#1-kerakli-narsalar)
2. [Deriv Hisob Ochish](#2-deriv-hisob-ochish)
3. [API Token Olish](#3-api-token-olish)
4. [Python O'rnatish](#4-python-ornatish)
5. [Bot O'rnatish](#5-bot-ornatish)
6. [Bot Sozlash](#6-bot-sozlash)
7. [Backtesting Qilish](#7-backtesting-qilish)
8. [Demo'da Test](#8-demoda-test)
9. [Real Accountga O'tish](#9-real-accountga-otish)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. KERAKLI NARSALAR

### 🖥️ Kompyuter Talablari
- **OS**: Windows 10/11, macOS, yoki Linux
- **RAM**: Minimum 4GB (8GB tavsiya)
- **Internet**: Barqaror internet aloqa
- **Vaqt**: 30-60 daqiqa o'rnatish uchun

### 💰 Pul
- **Demo uchun**: $0 (bepul virtual pul)
- **Real uchun**: $50-500 (boshlang'ich uchun $100 tavsiya)

---

## 2. DERIV HISOB OCHISH

### 📝 Qadam-baqadam:

#### A. Website'ga kirish
1. Brauzeringizni oching
2. https://deriv.com ga kiring
3. **"Sign Up"** tugmasini bosing

#### B. Ro'yxatdan o'tish
1. Email addressingizni kiriting
2. Password yarating (kuchli bo'lsin!)
3. **"Create demo account"** ni tanlang
4. Emailingizni tasdiqlang

#### C. Hisob turlari
✅ **Demo Account** - Virtual pul, xavf yo'q (boshlash uchun)
⚠️ **Real Account** - Haqiqiy pul, xavfli (keyinroq)

**MUHIM**: Birinchi demo bilan boshlang!

---

## 3. API TOKEN OLISH

API Token - bu botingizning "kaliti". Bu bilan bot sizning accountingizga ulanadi.

### 📝 Qadam-baqadam:

#### A. Deriv'ga login qiling
1. https://app.deriv.com ga kiring
2. Email va parolingizni kiriting

#### B. API Token sahifasiga boring
1. O'ng yuqori burchakda **profilingiz** tugmasini bosing
2. **"API Token"** ni tanlang
3. Yoki to'g'ridan-to'g'ri: https://app.deriv.com/account/api-token

#### C. Token yaratish
1. **"Create new token"** tugmasini bosing
2. Token nomini kiriting, masalan: "TradeMate Bot"
3. **Scopes** (ruxsatlar) tanlang:
   - ✅ **Read** - Ma'lumot o'qish
   - ✅ **Trade** - Savdo qilish
   - ✅ **Trading information** - Savdo ma'lumotlari
   - ❌ **Payments** - TANLMANG (xavfli)
   - ❌ **Admin** - TANLMANG (kerak emas)

4. **"Create"** tugmasini bosing

#### D. Tokenni saqlang
1. Token ko'rinadi: `a1-bS3cD4eF5gH6iJ7kL8mN9oP0qR1s`
2. **DIQQAT**: Token faqat 1 marta ko'rinadi!
3. Uni xavfsiz joyga ko'chiring:
   - Notepad'ga yozing
   - Yoki **password manager** ishlatiqng
4. **HECH KIMGA BERMANG!** Bu sizning hisobingiz kaliti!

**Screenshot qiling!** Tokenni unutsangiz, yangisini yaratishingiz kerak.

---

## 4. PYTHON O'RNATISH

### A. Python bor-yo'qligini tekshirish

Terminalni oching va yozing:

```bash
python --version
```

yoki

```bash
python3 --version
```

Agar `Python 3.8.0` yoki yuqori ko'rinsa, tayyor! [5-qadamga o'ting](#5-bot-ornatish).

### B. Python o'rnatish

#### **Windows:**

1. https://python.org/downloads ga boring
2. **"Download Python 3.11"** tugmasini bosing
3. Yuklab olingan fayl ni oching
4. **MUHIM**: **"Add Python to PATH"** ni belgilang ✅
5. **"Install Now"** tugmasini bosing
6. Tugaguncha kuting

#### **macOS:**

```bash
# Homebrew o'rnatilgan bo'lsa:
brew install python@3.11

# Yoki rasmiy saytdan yuklab oling
# https://python.org/downloads
```

#### **Linux (Ubuntu/Debian):**

```bash
sudo apt update
sudo apt install python3.11 python3-pip python3-venv
```

### C. O'rnatilganini tekshiring

```bash
python --version
# Ko'rinishi kerak: Python 3.11.x
```

---

## 5. BOT O'RNATISH

### A. Kod yuklab olish

#### **Option 1: Git bilan (tavsiya)**

```bash
# 1. Terminal oching
# 2. Git bor-yo'qligini tekshiring:
git --version

# 3. Agar git bo'lmasa:
# Windows: https://git-scm.com/download/win dan yuklab oling
# Mac: brew install git
# Linux: sudo apt install git

# 4. Kod yuklab olish:
git clone https://github.com/davron-murodullaev/mindmate-bot.git
cd mindmate-bot
```

#### **Option 2: ZIP fayl bilan**

1. https://github.com/davron-murodullaev/mindmate-bot ga boring
2. **"Code"** tugmasini bosing
3. **"Download ZIP"** ni tanlang
4. ZIP faylni extract qiling
5. Terminal'da papkaga kiring:

```bash
cd /path/to/mindmate-bot
```

### B. Virtual Environment yaratish

**Nima uchun kerak?** Python kutubxonalarni alohida saqlash uchun.

```bash
# 1. Virtual environment yaratish:
python -m venv venv

# 2. Aktivlashtirish:

# Windows CMD:
venv\Scripts\activate

# Windows PowerShell:
venv\Scripts\Activate.ps1

# macOS/Linux:
source venv/bin/activate

# Ko'rinishi kerak: (venv) C:\...\mindmate-bot>
```

### C. Kutubxonalarni o'rnatish

```bash
# venv aktiv ekanligini tekshiring!
# Ko'rinishi: (venv) ...

pip install -r requirements.txt

# Bu 2-5 daqiqa oladi...
# Ko'p matn o'tadi - bu normal!
```

**Xatolik bo'lsa?**

```bash
# Pip'ni yangilang:
python -m pip install --upgrade pip

# Qayta urinib ko'ring:
pip install -r requirements.txt
```

---

## 6. BOT SOZLASH

### A. .env fayl yaratish

```bash
# 1. .env.example fayldan ko'chirish:

# Windows:
copy .env.example .env

# macOS/Linux:
cp .env.example .env
```

### B. .env faylni ochish

```bash
# Notepad bilan (Windows):
notepad .env

# TextEdit bilan (Mac):
open -a TextEdit .env

# nano bilan (Linux):
nano .env

# Yoki istalgan text editor:
# VSCode, Sublime Text, etc.
```

### C. Token qo'yish

`.env` fayldagi `DERIV_API_TOKEN` ni o'zgartiring:

**OLDIN:**
```env
DERIV_API_TOKEN=your_deriv_api_token_here
```

**KEYIN:** (sizning tokeningiz bilan)
```env
DERIV_API_TOKEN=a1-bS3cD4eF5gH6iJ7kL8mN9oP0qR1s
```

### D. Sozlamalarni tekshirish

`.env` fayl quyidagicha bo'lishi kerak:

```env
# Deriv API Configuration
DERIV_API_TOKEN=a1-bS3cD4eF5gH6iJ7kL8mN9oP0qR1s  # SIZNING TOKENINGIZ
DERIV_APP_ID=1089

# Account Settings
DEMO_MODE=true              # Demo account ishlatish
INITIAL_STAKE=10.0          # Har bir savdoda $10

# Trading Parameters
TRADING_SYMBOL=R_100        # Volatility 100
CANDLE_INTERVAL=300         # 5 daqiqalik candle'lar
MIN_CONFIRMATIONS=3         # 3 signal kerak

# Risk Management
RISK_PER_TRADE=0.02         # 2% risk per trade
MAX_DAILY_LOSS=0.05         # 5% kunlik maksimal yo'qotish
MAX_CONSECUTIVE_LOSSES=3    # 3 marta ketma-ket yo'qotganda to'xta
MAX_TRADES_PER_DAY=10       # Kuniga maksimal 10 ta savdo

# Logging
LOG_LEVEL=INFO
```

**Faylni saqlang!** (Ctrl+S yoki Cmd+S)

---

## 7. BACKTESTING QILISH

**Backtesting** = Botni tarixiy ma'lumotlarda sinash

Bu **juda muhim**! Botni live'da ishga tushirishdan oldin, tarixiy datada qanday ishlashini ko'ring.

### A. Backtesting ishga tushirish

```bash
# venv aktiv bo'lishi kerak!
python -m backtesting.engine
```

### B. Nima bo'ladi?

Bot quyidagilarni qiladi:

1. ✅ Deriv'ga ulanadi
2. ✅ 5000 ta tarixiy candle yuklab oladi (R_100, 5min)
3. ✅ Strategiyani har bir candle'da test qiladi
4. ✅ Savdolarni simulatsiya qiladi
5. ✅ Natijalarni ko'rsatadi
6. ✅ `logs/backtest_results_*.json` ga saqlaydi

### C. Kutilgan natija

Terminal'da quyidagicha ko'rinadi:

```
============================================================
STARTING BACKTEST
============================================================
Initial Balance: $1000.00
Data Points: 5000
Date Range: 2024-01-01 00:00:00 to 2024-12-16 12:00:00
============================================================

Progress: 20.0% | Balance: $1050.20 | Trades: 3
Progress: 40.0% | Balance: $1080.50 | Trades: 8
...

✓ Trade #12 | BUY | P&L: $+15.30 (+1.45%) | Reason: Take Profit
✗ Trade #13 | SELL | P&L: $-10.20 (-0.98%) | Reason: Stop Loss
...

============================================================
BACKTEST RESULTS
============================================================
Initial Balance:    $1000.00
Final Balance:      $1250.30
Total P&L:          $+250.30 (+25.03%)
============================================================
Total Trades:       45
Winning Trades:     27
Losing Trades:      18
Win Rate:           60.00%
============================================================
Profit Factor:      2.15
Max Drawdown:       12.50%
Sharpe Ratio:       1.85
============================================================
Performance Rating: ⭐⭐⭐⭐ GOOD
============================================================
```

### D. Natijalarni tahlil qilish

**Yaxshi natija:**
- ✅ Win Rate > 50%
- ✅ Profit Factor > 1.5
- ✅ Total P&L > 10%
- ✅ Max Drawdown < 20%
- ✅ Rating: ⭐⭐⭐⭐ yoki ⭐⭐⭐⭐⭐

**Yomon natija:**
- ❌ Win Rate < 40%
- ❌ Profit Factor < 1.2
- ❌ Total P&L < 0% (zarar)
- ❌ Max Drawdown > 30%
- ❌ Rating: ⭐ yoki ⭐⭐

Agar natija yomon bo'lsa, sozlamalarni o'zgartiring (`.env` faylda).

---

## 8. DEMO'DA TEST

**DIQQAT**: Backtesting yaxshi bo'lsa ham, demo'da test qiling!

### A. Bot ishga tushirish (Demo)

```bash
# venv aktiv bo'lishi kerak!
python -m trading.bot --symbol R_100 --stake 10 --demo
```

### B. Nima bo'ladi?

Terminal'da quyidagicha ko'rinadi:

```
🚀 Starting TradeMate Bot...
============================================================
✓ Connected to Deriv (DEMO Account)
  Balance: $10,000.00
  Symbol: R_100
  Candle Interval: 300s
  Initial Stake: $10.00
============================================================

🤖 Trading loop started
Monitoring market for signals...

✓ Loaded 300 candles
Waiting 60s before next check... | Balance: $10,000.00

🎯 BUY Signal | Confidence: 75.0%
   • Uptrend (EMA 50 > EMA 200)
   • Bullish momentum (RSI: 65.5, MACD+)
   • Price above SMA20 (100.45 > 100.20)
   • Good volatility (ATR: 0.25%, ADX: 28.5)

📈 Placing BUY trade...
   Entry: 100.4500
   Stop Loss: 99.9500
   Take Profit: 101.2000
   Position Size: $20.00

✓ Trade executed | Contract ID: 123456789

✓ Position closed | P&L: $+15.30
✓ Trade WIN: $+15.30 | Balance: $10,015.30

Waiting 60s before next check... | Balance: $10,015.30
...
```

### C. Bot to'xtatish

Bot ishlab turganida:

```
Ctrl + C
```

Bot quyidagilarni qiladi:

1. ✅ Ochiq pozitsiyani yopadi (agar bor bo'lsa)
2. ✅ Barcha statistikani ko'rsatadi
3. ✅ Trade log'ni `logs/trades_*.json` ga saqlaydi
4. ✅ To'xta ydi

### D. Demo'da qancha vaqt test qilish kerak?

**Tavsiya**:
- ⏱️ Minimum: 1 hafta
- ⏱️ Ideal: 2-4 hafta
- ⏱️ Optimal: 1-2 oy

**Nima uchun?**
- Har xil market holatlarini ko'rish uchun
- Botning barqarorligini tekshirish
- Strategiyani yaxshilash uchun

---

## 9. REAL ACCOUNTGA O'TISH

**⚠️⚠️⚠️ JUDA MUHIM OGOHLANTIRISH! ⚠️⚠️⚠️**

Real accountda haqiqiy pulingiz yo'qolishi mumkin!

### A. Shartlar

Real accountga o'tishdan oldin:

- ✅ Backtesting natijasi **yaxshi** bo'lishi kerak
- ✅ Demo'da kamida **2 hafta** profitable bo'lgan bo'lishingiz kerak
- ✅ Strategiyani **to'liq tushungan** bo'lishingiz kerak
- ✅ Risk management'ni **qabul qilgan** bo'lishingiz kerak
- ✅ Yo'qotishga **tayyor bo'lgan pul** bilan boshlang

**Agar biron-biri yo'q bo'lsa, demo'da qoling!**

### B. Real Account ochish

1. https://app.deriv.com ga kiring
2. **"Real Account"** ni tanlang
3. Hujjatlaringizni yuklang (KYC - Know Your Customer):
   - Passport yoki ID card
   - Address proof (hisob-kitob yoki bank statement)
4. Tasdiqlanishni kuting (1-3 kun)

### C. Pul kiriting

1. **"Cashier"** sahifasiga boring
2. **"Deposit"** ni tanlang
3. To'lov usulini tanlang:
   - Bank card
   - Crypto (Bitcoin, USDT, etc.)
   - E-wallet
4. **Boshlang'ich miqdor**: $100-500 (tavsiya $200)

**DIQQAT**: Faqat yo'qotishga tayyor bo'lgan pul kiriting!

### D. Bot sozlamalarini o'zgartirish

`.env` faylni oching va o'zgartiring:

```env
# Oldin:
DEMO_MODE=true

# Keyin:
DEMO_MODE=false

# Va stake'ni kamaytiring:
INITIAL_STAKE=5.0  # Real pul uchun kamroq
```

### E. Bot ishga tushirish (Real)

```bash
python -m trading.bot --symbol R_100 --stake 5 --real
```

**TASDIQLASH** so'raladi:

```
⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️
WARNING: You are about to use a REAL ACCOUNT with REAL MONEY!
Are you sure you want to continue? (yes/no)
⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️

>
```

**"yes"** deb yozing va Enter bosing.

### F. Monitoring qilish

Real accountda:

- ✅ Kuniga kamida 2-3 marta tekshiring
- ✅ Trade log'larni o'qing
- ✅ Statistikaga e'tibor bering
- ✅ Agar 3-5 marta ketma-ket yo'qotilsa, to'xtating!

---

## 10. TROUBLESHOOTING

### ❌ "DERIV_API_TOKEN not found"

**Sabab**: `.env` fayl topilmadi yoki API token kiritilmagan

**Yechim**:
```bash
# 1. .env fayl bor-yo'qligini tekshiring:
ls .env  # Windows: dir .env

# 2. Agar yo'q bo'lsa:
cp .env.example .env  # Windows: copy .env.example .env

# 3. .env faylga tokenni kiriting
notepad .env  # yoki boshqa editor
```

### ❌ "ModuleNotFoundError: No module named 'websockets'"

**Sabab**: Dependencies o'rnatilmagan

**Yechim**:
```bash
# 1. venv aktiv ekanligini tekshiring
# Ko'rinishi: (venv) ...

# 2. Agar aktiv emas bo'lsa:
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Dependencies o'rnatish:
pip install -r requirements.txt
```

### ❌ "Authorization failed"

**Sabab**: API token noto'g'ri yoki expired

**Yechim**:
1. Deriv'ga kiring: https://app.deriv.com/account/api-token
2. Tokenni tekshiring
3. Agar expired bo'lsa, yangi token yarating
4. `.env` faylga yangi tokenni kiriting

### ❌ "Connection timeout"

**Sabab**: Internet aloqa muammosi yoki Deriv server down

**Yechim**:
1. Internetni tekshiring
2. VPN o'chiriq ekanligini tekshiring (ba'zan VPN muammo qiladi)
3. Deriv status tekshiring: https://deriv.statuspage.io
4. 5-10 daqiqa kuting va qayta urinib ko'ring

### ❌ "Can't trade: Max consecutive losses (3) reached"

**Sabab**: Bot 3 marta ketma-ket yo'qotdi va risk management to'xtatdi

**Yechim**:
Bu **normal**! Risk management ishlayapti. 2 variant:

**Variant 1**: Kutib turish (tavsiya)
```python
# Botni to'xtating (Ctrl+C)
# 1-2 soat kutib, bozorni tahlil qiling
# Yana ishga tushiring
```

**Variant 2**: Statistikani reset qilish
```python
# Faqat strategiya yaxshi ekanligiga ishonchingiz bo'lsa!
# Kodda: risk_manager.reset_stats()
```

### ❌ Bot sekin ishlayapti

**Sabab**: Internet sekin yoki ko'p datalarni yuklab olmoqda

**Yechim**:
```python
# .env faylda candle count'ni kamaytiring:
# CANDLE_HISTORY=300  # 1000 o'rniga
```

### ❌ "Insufficient balance"

**Sabab**: Hisobda pul yetarli emas

**Yechim**:
1. Balansni tekshiring: `await api.get_balance()`
2. INITIAL_STAKE'ni kamaytiring (`.env` faylda)
3. Yoki pul kiriting (real account uchun)

---

## 🎉 TAYYOR!

Agar hammasi ishlasa, sizda ishlaydigan trading bot bor! 🚀

### Keyingi Qadamlar:

1. ✅ Demo'da test qiling (1-4 hafta)
2. ✅ Strategiyani o'rganing va yaxshilang
3. ✅ Risk management sozlamalarini optimizelashtiring
4. ✅ Trade log'larni tahlil qiling
5. ✅ Agar barqaror bo'lsa, real accountga o'ting

### Foydali Havolalar:

- 📚 Deriv API Docs: https://api.deriv.com
- 📈 TradingView: https://tradingview.com
- 📖 Trading Strategy Guide: `docs/STRATEGY.md`
- 🎓 Risk Management: `docs/RISK_MANAGEMENT.md`

---

## 💬 Savol-Javoblar

**Q: Qancha vaqtda foyda ko'raman?**
A: Trading - bu marathon, sprint emas. Demo'da 2-4 hafta test qiling. Real accountda oylik 5-15% foyda realistic.

**Q: Bot 24/7 ishlashi kerakmi?**
A: Yo'q. Botni 4-6 soat kuzatib, keyin to'xtatishingiz mumkin. Yoki serverda ishlatishingiz mumkin.

**Q: Necha pul bilan boshlash kerak?**
A: Demo - $0. Real - minimum $100, tavsiya $200-500.

**Q: Bot yo'qotadimi?**
A: Ha, ba'zan. Hech bir bot 100% ishlamaydi. Risk management muhim!

**Q: Strategiyani o'zgartirsam bo'ladimi?**
A: Ha! `.env` faylda parametrlarni o'zgartiring. Lekin birinchi backtest qiling!

---

**OMAD! Savollar bo'lsa yozing! 💪🚀**

**Davron Murodullaev**
GitHub: @davron-murodullaev
