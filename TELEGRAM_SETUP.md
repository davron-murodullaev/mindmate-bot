# Telegram Bot Sozlamalari

Bu fayl BotFather'da bot sozlashda yordam beradi.

## 1. Bot Commands sozlash

BotFather'da `/setcommands` buyrug'ini bering va quyidagilarni ko'chiring:

```
start - 🏠 Bosh menyu - botni ishga tushirish
help - ❓ Yordam - botdan foydalanish bo'yicha ma'lumot
mood - 😊 Kayfiyat - bugungi kayfiyatingizni belgilang
journal - 📝 Kundalik - fikrlaringizni yozing
meditate - 🧘 Meditatsiya - tinchlanish mashqlari
fitness - 💪 Fitness - jismoniy mashqlar
healer - 🌿 Shifokor - tabiiy tabobat maslahatlari
stats - 📊 Statistika - sizning statistikangizni ko'ring
lang - 🌍 Til - tilni o'zgartirish
reset - 🔄 Reset - suhbatni yangilash
```

## 2. Bot Description (ta'rif)

BotFather'da `/setdescription` buyrug'ini bering:

```
🌟 MindMate - Sizning shaxsiy JARVIS darajasidagi AI yordamchingiz!

Men sizga yordam bera olaman:
• 💬 Aqlli AI suhbatlari
• 🌿 Tabiiy shifokorlik maslahatlari
• 😊 Kayfiyat kuzatuvi
• 📝 Kundalik yozish
• 🧘 Meditatsiya va tinchlanish
• 💪 Fitness mashqlari
• 📊 Shaxsiy statistika
• ✨ Kunlik motivatsiya

🧠 Men sizni eslab qolaman va har doim yordamga tayyorman!

/start - Boshlash
```

## 3. Bot About (qisqa ta'rif)

BotFather'da `/setabouttext` buyrug'ini bering:

```
🌟 MindMate - JARVIS darajasidagi shaxsiy AI yordamchi. Ruhiy salomatlik, shifokorlik, fitness va motivatsiya!
```

## 4. Bot Short Description

BotFather'da `/setshortdescription` buyrug'ini bering:

```
🧠 Sizning shaxsiy AI yordamchingiz - ruhiy qo'llab-quvvatlash, shifokorlik va motivatsiya!
```

## 5. Bot Picture (rasm)

BotFather'da `/setuserpic` buyrug'ini bering va bot uchun profil rasmini yuklang.

Tavsiya:
- 512x512 px
- PNG/JPG format
- Bot logotipi yoki AI/psixologiya bilan bog'liq rasm

## 6. Inline Mode (ixtiyoriy)

Agar inline mode kerak bo'lsa:

BotFather'da `/setinline` buyrug'ini bering:

```
Search MindMate...
```

## 7. Privacy Mode

BotFather'da `/setprivacy`:

```
DISABLED - Guruh xabarlarini o'qish uchun
```

yoki

```
ENABLED - Faqat shaxsiy xabarlar uchun (tavsiya etiladi)
```

## 8. Group Admin Rights (ixtiyoriy)

Agar botni guruhda ishlatmoqchi bo'lsangiz:

BotFather'da `/setjoingroups`:

```
DISABLED - Bot guruhga qo'shilmaydi
```

yoki

```
ENABLED - Bot guruhga qo'shilishi mumkin
```

---

## Qo'shimcha sozlamalar:

### Bot Menu Button

BotFather'da `/setmenubutton` buyrug'ini bering va bot menu tugmasini sozlang.

### Gruppa privacy

`/setprivacy` - ENABLED (shaxsiy foydalanish uchun tavsiya)

---

## To'liq sozlash ketma-ketligi:

1. BotFather'ga `/mybots` yozing
2. Botingizni tanlang
3. "Edit Bot" ni bosing
4. Quyidagilarni ketma-ket sozlang:
   - Edit Commands → yuqoridagi commandslarni qo'shing
   - Edit Description → to'liq ta'rifni qo'shing
   - Edit About → qisqa ta'rifni qo'shing
   - Edit Botpic → rasm yuklang (ixtiyoriy)

---

## Test qilish:

1. Telegram'da botingizni toping
2. `/start` bosing
3. Barcha commandslar menu'da ko'rinishi kerak
4. Tugmalar ishlashini tekshiring

✅ Tayyor!
