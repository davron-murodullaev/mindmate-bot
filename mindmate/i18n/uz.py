"""
Uzbek translations
"""

TRANSLATIONS = {
    "welcome": "👋 *Salom! Men — MindMate.*\n\nMen sizning AI do'stingizman:\n🎓 Imtihonga tayyorgarlik\n💼 Karyera maslahati\n💬 Suhbat va ruhiy yordam\n⏰ Eslatmalar va kundalik\n\n_Menyudan tanlang yoki shunchaki yozing/gapiring — men sizni tushunaman._\n\nDavom etish bilan /privacy va /terms ga rozilik bildirasiz.\n\nAvval tilni tanlang:",

    "start": {
        "welcome_back": "👋 *Qaytib kelganingizdan xursandman, {name}!*\n\nNimadan boshlaymiz?",
    },

    "setup": {
        "complete": "✅ Sozlash tugallandi! Endi barcha funksiyalardan foydalanishingiz mumkin.",
        "choose_timezone": "Iltimos, vaqt zonangizni tanlang:",
    },

    "menu": {
        "main_menu": "🏠 *Bosh menyu*\n\nMenga shunchaki yozing yoki gapiring — men tushunaman.\nYoki quyidagi tugmalarni ishlating:",
        "exam": "🎓 Imtihon",
        "career": "💼 Karyera",
        "friends": "💝 Do'st topish",
        "profile": "👤 Mening profilim",
        "mood_tracking": "😊 Kayfiyat",
        "healer": "🌟 Shifokor",
        "journal": "📝 Kundalik",
        "productivity": "🎯 Samaradorlik",
        "reminders": "⏰ Eslatmalar",
        "stats": "📊 Statistika",
        "settings": "⚙️ Sozlamalar",
        "premium": "💎 Premium",
        "help": "❓ Yordam",
    },

    "profile": {
        "subtitle": "Quyidagi vositalardan birini tanlang:",
        "exam_view_btn": "🎓 Imtihon sozlamalari",
        "exam_setup_btn": "🎓 Imtihon Mentor — Sozlash",
        "career_view_btn": "💼 Karyera sozlamalari",
        "career_setup_btn": "💼 Karyera Coach — Sozlash",
        "friends_view_btn": "💝 Do'stlik profili",
        "friends_setup_btn": "💝 Do'st topish — Sozlash",
        "edit_btn": "✏️ Tahrirlash",
        "title": "{name}ning profili",
        "badge_premium": "💎 Premium",
        "badge_free": "🆓 Bepul",
        "empty_hint": "_Hali hech narsa sozlanmagan. Quyidagi tugmalardan birini tanlang._",
        "exam_not_found": "Imtihon profili topilmadi.",
        "career_not_found": "Karyera profili topilmadi.",
        "friends_not_found": "Do'stlik profili topilmadi.",
        "days_left": "{delta} kun qoldi",
        "exam_today": "Imtihon bugun! 💪",
        "exam_passed": "o'tgan",
        "no_entry": "kiritilmagan",
        "verified": "✅ Tasdiqlangan",
        "pending_verify": "⏳ Tasdiqlanmagan",
        "visible": "👁 Ko'rinmoqda",
        "hidden": "🙈 Yashirilgan",
        "exam_detail": {
            "title": "🎓 *Imtihon Profili*",
            "exam_type": "📌 Imtihon turi",
            "level": "🎯 Daraja",
            "subjects": "📚 Fanlar",
            "date": "📅 Imtihon sanasi",
            "daily_hours": "⏱ Kunlik o'qish: {hours} soat",
        },
        "career_detail": {
            "title": "💼 *Karyera Profili*",
            "status": "📊 Holat",
            "role": "🎯 Maqsad lavozim",
            "industry": "🏭 Soha",
            "experience": "⏱ Tajriba: {exp} yil",
            "skills": "🛠 Ko'nikmalar",
        },
        "friends_detail": {
            "title": "💝 *Do'stlik Profili*",
            "name": "👤 Ism",
            "age": "🎂 Yosh",
            "gender": "👥 Jins",
            "city": "📍 Shahar",
            "goal": "🎯 Maqsad",
            "interests": "🎵 Qiziqishlar",
            "bio": "📝 Bio",
            "status": "🛡 Holat",
        },
    },

    "exam": {
        "teaser": (
            "🎓 *Imtihon Mentor*\n\n"
            "Men sizga DTM, IELTS yoki magistraturaga puxta tayyorlanishda "
            "yordam beraman:\n\n"
            "🎯 Shaxsiy o'qish rejasi\n"
            "📚 Har fan bo'yicha savol-javob\n"
            "🧪 Test mashqlari\n"
            "💪 Stressni boshqarish\n\n"
            "Boshlash uchun anketangizni to'ldiring (1 daqiqa)."
        ),
        "start_btn": "✨ Boshlash",
        "select_type": "🎓 *Qaysi imtihonga tayyorlanyapsiz?*",
        "dtm_select_subjects": (
            "📚 *DTM tayyorgarligi*\n\n"
            "Qaysi fanlarni topshiryapsiz?\n"
            "Bir nechta tanlang, tugagach *Tasdiqlash* ni bosing."
        ),
        "confirm_btn": "✅ Tasdiqlash",
        "min_subject_warn": "Kamida 1 ta fan tanlang!",
        "select_level": (
            "🎯 Hozirgi darajangiz qanday?\n\n"
            "🌱 Boshlovchi — endi boshlayapman\n"
            "🌿 O'rta — bazasi bor, mustahkamlash kerak\n"
            "🌳 Yuqori — deyarli tayyorman, mukammallikka intilaman"
        ),
        "date_prompt": (
            "📅 *Imtihon sanasi*\n\n"
            "Imtihon qachon bo'lishini bilasizmi?\n\n"
            "Sanani quyidagicha yozing: `2026-06-15`\n"
            "(Yil-Oy-Kun formati)\n\n"
            "Yoki bilmasangiz `keyin` deb yozing."
        ),
        "date_past_error": "❌ Sana o'tgan kun. Iltimos, kelajakdagi sanani kiriting (`2026-06-15` shaklida).",
        "date_format_error": "❌ Sana noto'g'ri formatda. Misol: `2026-06-15`\n\nYoki `keyin` deb yozing.",
        "setup_done": "✅ *Profilingiz tayyor!*\n\nEndi men sizning shaxsiy mentoringizman. Keling boshlaymiz!",
        "menu": {
            "plan": "📅 Bugungi rejam",
            "chat": "💬 Savol-javob",
            "practice": "🧪 Test mashqi",
            "stress": "💪 Stress yengish",
            "my_profile": "📊 Mening profilim",
            "setup": "⚙️ Sozlash",
        },
        "plan_loading": "⏳ Bugungi rejangizni tuzayapman...",
        "plan_error": "Reja tuzilmadi. Qaytadan urinib ko'ring.",
        "chat_intro": (
            "💬 *Savol-javob rejimi*\n\n"
            "Endi har qanday savolingizni yozing — fanlar bo'yicha, "
            "vaqt boshqaruvi yoki imtihon strategiyasi haqida.\n\n"
            "Misollar:\n"
            "• Trigonometriyada cosx ning hosilasi nima?\n"
            "• 3 hafta ichida 10 ta mavzuga qanday tayyorgarlik ko'raman?\n"
            "• Imtihondan oldin tunda nima qilish kerak?\n\n"
            "Chiqish uchun /menu"
        ),
        "no_subjects_warn": "Avval profilni sozlang — fanlar tanlang.",
        "practice_select": "🧪 *Test mashqi*\n\nQaysi fan bo'yicha savol kerak?",
        "question_loading": "⏳ Savol tuzayapman...",
        "question_answer_prompt": "💡 Javobingizni yozing — men baholayman.",
        "question_error": "Savol tuzib bo'lmadi. Qaytadan urinib ko'ring.",
        "stress_intro": (
            "💪 *Stressni boshqarish*\n\n"
            "Imtihon yaqinlashganda nimani his qilyapsiz? Yozing — yordam beraman.\n\n"
            "Misol:\n"
            "• \"Hech narsa esimdan chiqyapti\"\n"
            "• \"Vaqt yetmaydi deb qo'rqaman\"\n"
            "• \"Ota-onam ko'p bosim qilyapti\""
        ),
        "dashboard_title": "🎓 *Imtihon Mentor*",
        "dashboard_prompt": "Bugun nima qilamiz?",
        "no_profile": "Avval imtihon profilini sozlang. /exam",
        "reset_confirm": "⚙️ *Profilni qayta sozlash*\n\nBu eski profilni o'chirib, yangi sozlashni boshlaydi. Davom etamizmi?",
        "reset_yes": "✅ Ha, qaytadan",
        "reset_cancel": "❌ Bekor qilish",
        "type": {
            "dtm": "📚 DTM (UZ universiteti)",
            "ielts": "🌍 IELTS (ingliz tili)",
            "sat": "🇺🇸 SAT (chet el)",
            "magistratura": "🎓 Magistratura",
            "cefr": "📜 CEFR sertifikati",
        },
        "level": {
            "beginner": "🌱 Boshlovchi",
            "intermediate": "🌿 O'rta",
            "advanced": "🌳 Yuqori",
        },
        "edit": {
            "title": "🎓 *Imtihon profilini tahrirlash*",
            "what_to_change": "Qaysi ma'lumotni o'zgartirmoqchisiz?",
            "field_type": "📌 Imtihon turi",
            "field_subjects": "📚 Fanlar",
            "field_level": "🎯 Daraja",
            "field_date": "📅 Imtihon sanasi",
            "change_type": "🎓 *Imtihon turini o'zgartiring:*",
            "change_subjects": "📚 *Fanlarni o'zgartiring:*\n\nKerakli fanlarni tanlang, so'ng Saqlash.",
            "change_level": "🎯 *Darajangizni o'zgartiring:*",
            "enter_date": "📅 *Imtihon sanasini kiriting:*\n\nFormat: `2026-06-15` (Yil-Oy-Kun)\nO'chirish uchun `o'chir` deb yozing.",
            "save_btn": "✅ Saqlash",
            "date_updated": "✅ Imtihon sanasi yangilandi!",
            "date_past_error": "❌ Sana o'tgan. Kelajakdagi sanani kiriting (`2026-06-15`).",
            "date_format_error": "❌ Noto'g'ri format. Misol: `2026-06-15`\nYoki o'chirish uchun `o'chir` deb yozing.",
        },
    },

    "career": {
        "teaser": (
            "💼 *Karyera Coach*\n\n"
            "Men sizga yaxshi ish topish va karyerada o'sishda yordam beraman:\n\n"
            "📝 ATS-friendly resume yaratish\n"
            "🎤 Intervyuga tayyorgarlik\n"
            "💰 Maoshni qanday so'rashni o'rganish\n"
            "📈 6 oylik karyera rejasi\n\n"
            "Boshlash uchun anketani to'ldiring (1 daqiqa)."
        ),
        "start_btn": "✨ Boshlash",
        "select_status": "💼 *Hozirgi holatingizni tanlang:*",
        "enter_role": (
            "🎯 *Maqsad lavozim*\n\n"
            "Qaysi lavozimda ishlamoqchisiz?\n\n"
            "Misollar:\n"
            "• Frontend Developer\n"
            "• HR Manager\n"
            "• Marketing Specialist\n"
            "• Sotuv menejeri\n"
            "• Buxgalter\n\n"
            "Yozing:"
        ),
        "enter_exp": (
            "⏱ *Tajribangiz necha yil?*\n\n"
            "Faqat raqam kiriting (masalan: `0`, `2`, `5`).\n"
            "Talaba yoki bitiruvchi bo'lsangiz `0` yozing."
        ),
        "exp_invalid": "❌ Iltimos, 0 dan 60 gacha bo'lgan raqam kiriting.",
        "setup_done": "✅ *Profilingiz tayyor!*\n\nEndi men sizning shaxsiy karyera koachingizman. Qani boshlaymiz!",
        "menu": {
            "resume": "📝 Resume yaratish",
            "review": "🔍 Resume tahlili",
            "interview": "🎤 Intervyu mashqi",
            "chat": "💬 Maslahat olish",
            "salary": "💰 Maosh muzokarasi",
            "plan": "📈 Karyera rejasi",
            "my_profile": "⚙️ Profilim",
        },
        "resume_intro": (
            "📝 *Resume yaratish*\n\n"
            "Resume yozib beraman! Quyidagi ma'lumotlarni *bitta xabarda* yozing:\n\n"
            "1️⃣ *Ism familiya, telefon, email*\n"
            "2️⃣ *Ta'lim* (universitet, fakultet, yil)\n"
            "3️⃣ *Ish tajribasi* (kompaniya, lavozim, yil, asosiy ishlar)\n"
            "4️⃣ *Ko'nikmalar* (texnik + tillar)\n"
            "5️⃣ *Loyiha/sertifikatlar* (agar bor bo'lsa)\n\n"
            "Hammasini erkin shaklda yozing — men professional resume'ga aylantiraman."
        ),
        "review_intro": (
            "🔍 *Resume tahlili*\n\n"
            "Hozirgi resume'ingizni shu yerga *to'liq* yozing yoki ko'chirib paste qiling.\n\n"
            "Men quyidagilarga e'tibor beraman:\n"
            "✓ ATS-friendly emasmi (robot tushunarmi)\n"
            "✓ Action verb va raqamlar\n"
            "✓ Format va tuzilish\n"
            "✓ Yaxshilash kerak bo'lgan joylar\n\n"
            "Resume'ni yozing:"
        ),
        "chat_intro": (
            "💬 *Karyera bo'yicha maslahat*\n\n"
            "Har qanday savolingizni yozing:\n\n"
            "Misollar:\n"
            "• \"3 yil tajriba bilan qancha maoshi so'rasam bo'ladi?\"\n"
            "• \"IT sohaga qanday o'tsam bo'ladi?\"\n"
            "• \"LinkedIn profilim'ni qanday yaxshilash kerak?\"\n"
            "• \"Boshliqdan oshirish so'rashning to'g'ri yo'li nima?\""
        ),
        "salary_intro": (
            "💰 *Maosh muzokarasi*\n\n"
            "Quyidagilardan birini yozing:\n\n"
            "1. \"Hozir X so'm olaman, oshirish so'rasam bo'ladimi?\"\n"
            "2. \"Yangi ishga ofer berishdi, qanday kelishaman?\"\n"
            "3. \"Bozorda mening lavozim qancha to'lanadi?\"\n\n"
            "Aniq raqamlar va vaziyatni yozsangiz, aniq strategiya beraman."
        ),
        "plan_intro": (
            "📈 *6 oylik karyera rejasi*\n\n"
            "Aytib bering: hozirda qaysi bosqichdasiz va 6 oydan keyin "
            "qayerda bo'lishni xohlaysiz?\n\n"
            "Misol:\n"
            "_\"Hozir junior frontend, 6 oyda middle bo'lishni xohlayman\"_\n\n"
            "Men sizga aniq qadamlardan iborat reja tuzib beraman:\n"
            "• Qaysi ko'nikmani o'rganasiz\n"
            "• Qaysi loyiha qilasiz\n"
            "• Qaysi kursni olasiz\n"
            "• Qachon ish o'zgartirasiz\n\n"
            "Yozing:"
        ),
        "dashboard_title": "💼 *Karyera Coach*",
        "dashboard_prompt": "Bugun nima qilamiz?",
        "no_profile": "Avval karyera profilini sozlang. /career",
        "reset_confirm": "⚙️ *Profilni qayta sozlash*\n\nEski profilni o'chirib, qaytadan boshlaymizmi?",
        "reset_yes": "✅ Ha, qaytadan",
        "reset_cancel": "❌ Bekor qilish",
        "interview": {
            "select": "🎤 *Intervyu mashqi*\n\nQaysi turdagi savol bilan boshlaymiz?",
            "general": "👋 Umumiy savol (HR)",
            "technical": "🛠 Texnik savol",
            "behavioral": "⭐ Behavioral (STAR)",
            "loading": "⏳ Savol tayyorlanyapti...",
            "answer_prompt": "💬 Javobingizni yozing — men professional baholashni beraman.",
            "error": "Savol tuzib bo'lmadi.",
            "another": "🎤 Yana savol",
            "evaluating": "🎯 Javobingizni baholayapman...",
        },
        "resume_loading": "⏳ Resume yarataman, biroz kuting...",
        "review_loading": "🔍 Resume'ni tahlil qilyapman...",
        "status": {
            "student": "🎓 Talaba",
            "graduate": "🎯 Bitiruvchi (ish izlamoqdaman)",
            "employed": "💼 Hozir ishlayapman",
            "switching": "🔄 Ish o'zgartirmoqchiman",
            "freelance": "🚀 Freelancer / Biznes",
        },
        "edit": {
            "title": "💼 *Karyera profilini tahrirlash*",
            "what_to_change": "Qaysi ma'lumotni o'zgartirmoqchisiz?",
            "field_status": "📊 Holat",
            "field_role": "🎯 Maqsad lavozim",
            "field_experience": "⏱ Tajriba yillari",
            "change_status": "📊 *Hozirgi holatni o'zgartiring:*",
            "enter_role": "🎯 *Maqsad lavozimni o'zgartiring:*\n\nYangi lavozimni yozing:",
            "enter_experience": "⏱ *Tajribani o'zgartiring:*\n\nNecha yil tajribangiz bor? (raqam yozing)",
            "role_updated": "✅ Maqsad lavozim yangilandi!",
            "exp_updated": "✅ Tajriba yangilandi!",
        },
    },

    "voice": {
        "too_large": "🎙 Ovozli xabar juda katta (25 MB dan oshiq). Iltimos, qisqaroq xabar yuboring.",
        "not_understood": "🎙 Ovozli xabarni tushunolmadim. Iltimos, sekinroq va aniqroq qayta ayting yoki matn ko'rinishida yozib yuboring.",
        "heard": "🎙 _Eshitganim:_ {text}",
        "error": "🎙 Ovozni o'qishda xatolik. Matn ko'rinishida yozib yuboring.",
    },

    "general": {
        "cancel_done": "✅ Bekor qilindi.",
    },

    "friends": {
        "teaser": (
            "💝 *Do'st topish*\n\n"
            "Yangi tanishuvlar va mazmunli munosabatlar uchun MindMate joyi.\n\n"
            "✨ *Sodda anketa* — 1 daqiqada to'ldiriladi\n"
            "🎯 *Aqlli mos topish* — qiziqish va shaharingiz bo'yicha\n"
            "💬 *Telegram'da to'g'ridan-to'g'ri suhbat* — alohida ilova kerak emas\n"
            "🎭 *3 turdagi tanishuv* — do'stlik, munosabat, hamkorlik\n"
            "🔒 *Faqat 18+* — xavfsiz muhit\n"
            "👁 *Sizni xohlasangiz yashiradi* — istalgan vaqt anketani o'chirib qo'ying\n\n"
            "Anketangizni to'ldiring — yangi do'stlar topish vaqti!"
        ),
        "dashboard_title": "💝 *Do'st topish*",
        "dashboard_prompt": "_Bugun yangi tanishuv?_",
        "likes_text": "💖 Sizni yoqtirganlar: *{count}*",
        "likes_premium_hint": " _(Premium'da kim ekanligi ko'rinadi)_",
        "verified_badge": "✅ Tasdiqlangan",
        "not_verified_badge": "🔓 Tasdiqlanmagan",
        "visibility_active": "👁 Ko'rinmoqda",
        "visibility_hidden": "🙈 Yashirin",
        "btn_browse": "💝 Tanishuv boshlash",
        "btn_myprofile": "✨ Mening anketam",
        "btn_matches": "💌 Match'lar",
        "btn_likes": "💖 Sizni yoqtirganlar",
        "btn_filters": "🎯 Filtrlar",
        "btn_edit": "⚙️ Tahrirlash",
        "btn_hide": "🙈 Anketani yashirish",
        "btn_show": "👁 Anketani ko'rsat",
        "btn_verified": "✅ Tasdiqlangan",
        "btn_verify_start": "🛡 Anketani tasdiqlash",
        "btn_pass": "❌ O'tib ketish",
        "btn_like": "❤️ Yoqdi",
        "btn_block": "🚫 Bloklash",
        "btn_stop_browse": "⏸ Tanishuvni to'xtatish",
        "btn_continue_browse": "➡️ Tanishuvni davom ettirish",
        "btn_write": "💬 Telegram'da yozish",
        "btn_icebreakers": "💡 Suhbat boshlovchi savollar",
        "btn_create": "✨ Anketa yaratish",
        "btn_ai_bio": "✨ AI bio yozib bersin",
        "btn_skip_bio": "⏭ Bio'siz davom etish",
        "btn_skip_photos": "⏭ Rasmsiz davom etish",
        "btn_edit_photos": "📸 Faqat rasmlarni o'zgartirish",
        "btn_edit_full": "📝 Anketani to'liq qayta yozish",
        "btn_change_photos": "📸 Rasmlarni o'zgartirish",
        "btn_full_edit": "✏️ To'liq tahrirlash",
        "btn_clear_photos": "🗑 Boshqatdan boshlash",
        "btn_confirm_photos": "✅ Tasdiqlash ({count}/{max} rasm)",
        "btn_confirm_interests": "✅ Tasdiqlash ({count}/{max} qiziqish)",
        "btn_gender_male": "👨 Erkak",
        "btn_gender_female": "👩 Ayol",
        "btn_gender_any": "🌈 Hammasi",
        "btn_get_premium": "💎 Premium olish",
        "btn_start_browsing": "💝 Tanishuv boshlash",
        "pref_any": "Hammasi",
        "pref_yes": "Ha",
        "pref_no": "Yo'q",
        "pref_title": "🎯 *Filtrlar*\n\n_Tanishuv bo'limida ko'rinadigan odamlarni cheklash uchun:_",
        "pref_gender_btn": "👤 Jins: {label}",
        "pref_age_btn": "🎂 Yosh oraligi: {label}",
        "pref_city_btn": "📍 Faqat shahrim: {label}",
        "pref_gender_title": "👤 *Kimni izlayapsiz?*",
        "pref_age_title": "🎂 *Yosh oralig'ini kiriting*\n\nFormat: `min-max`\nMisol: `20-30` yoki `18-100`",
        "pref_age_error": "❌ Format noto'g'ri. Misol: `20-30` (18-100 oralig'ida)",
        "pref_age_updated": "✅ Yosh oralig'i yangilandi.",
        "edit_title": "✏️ *Tahrirlash*\n\nNimani o'zgartirmoqchisiz?",
        "wizard_name": "✨ *Anketa yaratish*\n\nAvval ismingizni kiriting (Telegram'dagi ismingiz yoki taxallus):",
        "wizard_age": "🎂 *Yoshingiz?*\n\nFaqat raqam yozing (masalan: `22`).\n_Bot {min_age}+ yosh foydalanuvchilar uchun._",
        "wizard_looking": "🎯 *Nima izlayapsiz?*",
        "wizard_gender": "👤 *Jinsingizni tanlang*\n\n_(Boshqa foydalanuvchilar sizni shunga qarab topishadi)_",
        "wizard_city": "🌆 *Shahringiz qaysi?*\n\nIltimos, shahar nomini yozing.\n_Misol: Toshkent, Samarqand, Buxoro_",
        "wizard_interests": "✨ *Qiziqishlaringizni tanlang*\n\nKamida {min} ta, ko'pi bilan {max} ta:",
        "wizard_bio": "✨ *O'zingiz haqingizda qisqa yozing*\n\n1-3 jumla — kim ekanligingiz va qanday odamni qidirayapsiz.\n\n_Maksimum {max_len} ta belgi._\n\nYoki AI'dan yordam oling:",
        "wizard_photos": "📸 *Profilingizga rasm qo'shing*\n\n1 dan {max} tagacha rasm yuborishingiz mumkin. Birinchi rasm asosiy bo'ladi.\n\n_Rasmni galereya iconi orqali yuboring (skrepka emas)._",
        "wizard_done": "🎉 *Anketangiz tayyor!*\n\nEndi siz boshqalarni ko'rasiz va ular ham sizni topadi.\n_Maslahat: anketani tasdiqlasangiz 3x ko'proq match olasiz._",
        "wizard_ai_bio_loading": "✨ Bio yozyapman...",
        "wizard_ai_bio_done": "✨ *Sizning bio:*\n\n_{bio}_\n\n📸 Endi 1 dan {max} tagacha rasm yuboring (birinchi rasm asosiy bo'ladi):",
        "wizard_ai_bio_error": "_Bio yaratib bo'lmadi, davom etamiz._",
        "photo_accepted": "✅ {count}/{max} rasm qabul qilindi.\n\nYana yuborishingiz mumkin yoki tasdiqlang:",
        "photo_max_error": "❌ Maksimum {max} ta rasm. Tasdiqlash tugmasini bosing yoki boshqatdan boshlang.",
        "photo_cleared": "🗑 Hammasi tozalandi.\n\nYangidan 1 dan {max} tagacha rasm yuboring:",
        "photos_saved": "✅ *{count} ta rasm saqlandi!*",
        "error_save": "❌ Anketani saqlashda xatolik. Iltimos, qaytadan urinib ko'ring.",
        "error_photos_save": "❌ Rasmlarni saqlashda xatolik. Qaytadan urinib ko'ring.",
        "error_doc_convert": "❌ Rasmni qayta ishlashda xatolik. Iltimos, *rasm* sifatida qaytadan yuboring (kamera/galereya iconi).",
        "error_moderation": "❌ *Bu rasmni qabul qila olmayman.*",
        "error_moderation_suffix": "\n\nIltimos, boshqa rasm yuboring.",
        "validation_name": "❌ Ism 2-50 ta belgi bo'lishi kerak.",
        "validation_age": "❌ Yoshi {min} dan {max} gacha bo'lishi kerak.",
        "validation_gender": "Iltimos, jinsingizni tanlang",
        "validation_city": "❌ Shahar nomi 2-100 ta belgi bo'lishi kerak.",
        "validation_interests_min": "Kamida {min} ta qiziqish tanlang!",
        "validation_interests_max": "Maksimum {max} ta tanlay olasiz",
        "validation_bio": "❌ Bio juda uzun ({length} ta belgi). Maksimum {max} ta.",
        "browse_no_profiles": "🔍 *Hozircha mos anketalar yo'q*\n\nFiltrlarni kengaytirib ko'ring yoki keyinroq qaytib tekshiring.",
        "browse_like_quota": "🚫 *Bugungi like chegarasi tugadi* ({limit} ta).\n\n💎 *Premium*'ga o'tib cheksiz like bering!",
        "browse_like_limit_answer": "Bugungi {limit} like chegarasi tugadi. Premium'ga o'ting.",
        "browse_blocked_answer": "Foydalanuvchi bloklandi",
        "match_text": "🎉 *Match!*\n\nSiz va {name} bir-biringizni yoqtirdingiz!\n\n💬 To'g'ridan-to'g'ri Telegram'da yozishingiz mumkin yoki AI'dan suhbat boshlovchi savollarni so'rang.",
        "photo_count": "📸 _{count} ta rasm_",
        "icebreakers_title": "💡 *Suhbat boshlovchi savollar:*\n\n",
        "icebreakers_loading": "AI savollarni tayyorlayapti...",
        "icebreakers_error": "Texnik xatolik.",
        "myprofile_title": "👤 *Mening anketam:*\n\n",
        "matches_empty": "💌 *Match'lar*\n\nHozircha match'lar yo'q. Tanishuv bo'limida boshqa anketalarni ko'ring!",
        "matches_title": "💌 *Sizning match'laringiz:*\n",
        "likes_none": "💖 *Sizni yoqtirganlar*\n\nHozircha hech kim yoqtirmagan. Anketani sifatliroq qiling, rasmni tasdiqlang — match'lar oshadi!",
        "likes_count_free": "💖 *Sizni yoqtirganlar: {count}*\n\nKim ekanligini ko'rish uchun 💎 *Premium*'ga o'ting.",
        "likes_count_premium": "💖 *Sizni yoqtirganlar: {count}*\n",
        "likes_later": "_Yangilash uchun keyinroq qayting._",
        "hide_answer": "Anketa yashirildi",
        "show_answer": "Anketa ko'rinmoqda",
        "verify_no_photo": "❌ Avval profilingizga rasm qo'shing — keyin tasdiqlay olasiz.",
        "verify_intro": "🛡 *Anketani tasdiqlash*\n\nHozir bizga *yangi selfie* yuboring — yuzingizni aniq ko'rsatadigan, yorug' joyda olingan rasm.\n\nAI selfini sizning anketa rasmingiz bilan solishtirib, ✅ *Tasdiqlangan* belgisini beradi.\n\n_(Tasdiqlangan profillar 3x ko'proq match oladi.)_",
        "verify_loading": "🔍 AI tasdiqlamoqda...",
        "verify_success": "✅ *Tasdiqlandi!*\n\n_{note}_\n\nEndi anketangizda \"✅ Tasdiqlangan\" belgisi paydo bo'ladi va siz 3x ko'proq ko'rinasiz.",
        "verify_fail": "❌ *Tasdiqlanmadi.*\n\n_{note}_\n\nYorug' joyda yangi selfie bilan qaytadan urinib ko'ring.",
        "verify_error": "Tasdiqlashda xatolik. Qaytadan urinib ko'ring.",
        "verify_no_saved": "❌ Avval profil rasmini qo'shing.",
        "verified_info": "✅ Sizning anketangiz tasdiqlangan! 3x ko'proq ko'rinadi.",
    },

    "mood": {
        "select": "Bugun o'zingizni qanday his qilyapsiz?",
        "logged": "✅ Kayfiyat saqlandi!",
        "happy": "Xursand",
        "sad": "G'amgin",
        "angry": "Jahldor",
        "anxious": "Tashvishli",
        "tired": "Charchagan",
        "excited": "Hayajonli",
        "stats": "📊 So'nggi {days} kundagi kayfiyat statistikasi:",
        "no_data": "Hali kayfiyat ma'lumotlari yo'q. Birinchi kayfiyatingizni kiriting!",
    },

    "healer": {
        "welcome": "🌟 Shifokor rejimiga xush kelibsiz\n\nMen sizni tinglash va qo'llab-quvvatlash uchun shu yerdaman. Fikrlaringiz bilan bo'lishing.\n\nXabaringizni quyida yozing:",
        "active": "🌟 Shifokor rejimi faol\n\nMen tinglayapman. Fikr va his-tuyg'ularingiz bilan bo'lishing:",
        "exit": "Bo'lishganingiz uchun rahmat. O'zingizga yaxshilik qiling! 💚",
        "crisis": "Sizning hayotingiz qadrli. Iltimos, darhol professional yordamga murojaat qiling:\n\n🆘 Tez yordam:\n• 1050 (O'zbekiston ishonch telefoni)\n• 103 (Tez tibbiy yordam)\n\nYolg'iz emassiz. 💚",
    },

    "journal": {
        "welcome": "📝 Kundalik\n\nNima qilmoqchisiz?",
        "new_entry": "✍️ Yangi yozuv",
        "view_entries": "📖 Yozuvlarni ko'rish",
        "enter_text": "Kundalik yozuvingizni yozing:\n\n(Xohlaganingizcha yozishingiz mumkin)",
        "saved": "✅ Yozuv saqlandi!",
        "no_entries": "Sizda hali kundalik yozuvlari yo'q.",
        "entry": "📝 {date} dagi yozuv:\n\n{content}",
    },

    "productivity": {
        "welcome": "🎯 Samaradorlik murabbiysi\n\nMen sizga maqsadlaringizga erishish va samaradorlikni oshirishda yordam berish uchun shu yerdaman!\n\nBugun qanday yordam bera olaman?",
        "active": "🎯 Samaradorlik rejimi faol\n\nVazifalaringiz, maqsadlaringiz bilan bo'lishing yoki samaradorlik bo'yicha maslahat so'rang:",
    },

    "stats": {
        "welcome": "📊 Sizning statistikangiz\n\nNimani ko'rmoqchisiz?",
        "mood": "😊 Kayfiyat statistikasi",
        "journal": "📝 Kundalik statistikasi",
        "overall": "📈 Umumiy statistika",
        "summary": "📊 Umumiy statistika ({days} kun):\n\n• Kayfiyat yozuvlari: {moods}\n• Kundalik yozuvlari: {journals}\n• AI suhbatlar: {chats}",
    },

    "reminders": {
        "welcome": "⏰ *Eslatmalar*\n\nMen sizga vaqtida eslatib turaman.",
        "new": "➕ Yangi eslatma",
        "list": "📋 Mening eslatmalarim",
        "delete_all": "🗑 Barchasini o'chirish",
        "delete_one": "🗑 O'chirish",
        "delete_all_confirm": "⚠️ Barcha faol eslatmalar o'chiriladi. Davom etamizmi?",
        "all_deleted": "✅ Barcha eslatmalar o'chirildi.",
        "deleted": "✅ Eslatma o'chirildi.",
        "tap_to_delete": "_O'chirish uchun yuqoridagi tugmalarni bosing._",
        "list_header": "📋 *Sizning eslatmalaringiz:*",
        "set": "⏰ *Eslatma o'rnatish*\n\nMenga qachon va nima haqida eslatishim kerakligini ayting.\n\nMisol: _Ertaga soat 15:00 da suv ichishni eslatib tur_",
        "created": "✅ *Eslatma yaratildi!*\n\n📌 _{text}_\n⏰ {time}",
        "notification": "⏰ Eslatma: {text}",
        "no_reminders": "📭 Sizda faol eslatmalar yo'q.",
        "list_item": "• {time} — _{text}_",
        "limit_reached": "❌ Bepul rejimda maksimum {limit} eslatma mumkin. Premium'ga o'ting!",
        "parse_error": "❌ Vaqtni tushunmadim. Iltimos, qayta urinib ko'ring.\n\nMisol: _Ertaga 15:00 da yig'ilish_",
    },

    "settings": {
        "welcome": "⚙️ Sozlamalar",
        "language": "🌐 Til",
        "timezone": "🕐 Vaqt zonasi",
        "delete_data": "🗑 Ma'lumotlarimni o'chirish",
        "delete_confirm": "⚠️ Barcha ma'lumotlaringiz o'chiriladi. Davom etasizmi?",
        "delete_done": "✅ Ma'lumotlaringiz o'chirildi.",
    },

    "premium": {
        "welcome": "💎 Premium obuna\n\nPremium imkoniyatlar:\n\n✅ Cheksiz AI suhbatlar\n✅ Cheksiz eslatmalar\n✅ Chuqur statistika\n✅ Ovozli xabarlar\n✅ Birinchi navbatda javob\n\nNarxi: 25 000 so'm/oy",
        "subscribe_stars": "⭐ Telegram Stars (200⭐)",
        "subscribe_card": "💳 Karta orqali to'lash",
        "active": "✅ Premium obunangiz faol! Tugash sanasi: {date}",
        "limit_reached": "❌ Bugungi bepul limit tugadi ({limit} ta xabar). Premium'ga o'ting!",
    },

    "payments": {
        "premium_title": "💎 *MindMate Premium*",
        "premium_benefits": "*Premium afzalliklari:*\n✅ Cheksiz AI suhbatlar\n✅ Cheksiz eslatmalar va kundalik\n✅ Do'st topish: cheksiz like\n✅ Sizni yoqtirgan odamlarni ko'rish\n✅ Premium nishon (✨)\n✅ Birinchi navbatda javob",
        "select_plan": "*Rejani tanlang:*",
        "already_premium": "✅ *Sizda allaqachon Premium bor!*\n\nTugash sanasi: *{expires}*\n\nYana bir muddat qo'shmoqchimisiz? Quyidagi rejalarni tanlang:",
        "plan_1m_label": "💎 Premium — 1 oy",
        "plan_3m_label": "💎 Premium — 3 oy",
        "plan_12m_label": "💎 Premium — 12 oy",
        "plan_1m_desc": "1 oylik MindMate Premium",
        "plan_3m_desc": "3 oylik MindMate Premium (17% chegirma)",
        "plan_12m_desc": "12 oylik MindMate Premium (33% chegirma)",
        "unknown_plan": "Noma'lum reja",
        "invoice_error": "❌ To'lov rejasini yuborishda xatolik. Qaytadan urinib ko'ring.",
        "technical_error": "Texnik xatolik. Qaytadan urinib ko'ring.",
        "generic_error": "❌ Xatolik yuz berdi.",
        "unknown_plan_admin": "❌ Noma'lum reja. Adminga murojaat qiling.",
        "success": "🎉 *Premium faollashtirildi!*\n\n📅 Tugash sanasi: *{expires}*\n⭐ To'langan: *{stars} Stars*\n\nEndi cheksiz AI suhbatlari, cheksiz like'lar va boshqa imkoniyatlardan foydalanishingiz mumkin. Rahmat! 💎",
        "partial_success": "✅ To'lov muvaffaqiyatli, ammo tizimda kichik xato. Adminga murojaat qiling — Premium qo'lda yoqiladi.",
        "stars_payment_title": "⭐ *Telegram Stars to'lov*",
        "stars_payment_prompt": "Rejani tanlang:",
        "card_coming_soon": "💳 *Karta orqali to'lov tez orada qo'shiladi.*\n\nHozirgi vaqtda ⭐ Telegram Stars orqali to'lay olasiz — tez, sertifikatsiz, xavfsiz.",
    },

    "admin": {
        "no_access": "⛔ Bu komanda faqat adminlar uchun.",
        "stats_title": "📊 *MindMate Statistikasi*",
        "users_header": "*👥 Foydalanuvchilar*",
        "total": "Jami",
        "new_today": "Bugun yangi",
        "wau": "7 kun faol (WAU)",
        "mau": "30 kun faol (MAU)",
        "friends_header": "*💝 Do'st topish*",
        "profiles": "Anketa",
        "verified": "Tasdiqlangan",
        "likes": "Like'lar",
        "matches": "Match'lar",
        "modules_header": "*🎓 Boshqa modullar*",
        "exam_profiles": "Imtihon Mentor",
        "career_profiles": "Karyera Coach",
        "premium_header": "*💎 Premium*",
        "active_subs": "Faol obuna",
        "conversion": "Konvertatsiya",
        "ai_header": "*🤖 AI ishlatilishi*",
        "today": "Bugun",
        "week": "7 kun",
        "messages": "xabar",
        "error": "❌ Xatolik",
    },

    "legal": {
        "btn_terms": "📜 Foydalanish shartlari",
        "btn_privacy": "🔒 Maxfiylik siyosati",
        "btn_main_menu": "⬅️ Asosiy menyu",
        "privacy_text": "🔒 *Maxfiylik siyosati*\n\n*Yangilangan:* 2026\n\n*Biz qanday ma'lumotlarni yig'amiz?*\n• Telegram ID, ism, til\n• Anketa ma'lumotlari (yosh, shahar, qiziqishlar, rasm)\n• AI suhbatlar (xizmatni yaxshilash uchun)\n• Eslatma, kayfiyat, kundalik yozuvlari\n\n*Qanday foydalanamiz?*\n• Sizga AI javoblari va tavsiyalar berish\n• Do'st topish bo'limida mos kelishlarni qidirish\n• Bot funksiyalarini yaxshilash\n\n*Uchinchi tomonlar:*\n• OpenAI — AI javoblari uchun (anonim, sizning shaxsiy ma'lumotlaringizsiz)\n• Telegram — xabar yuborish uchun\n• Boshqa hech kim\n\n*Sizning huquqlaringiz:*\n• Ma'lumotlaringizni istalgan vaqt o'chirish (Sozlamalar → 🗑 Ma'lumotlarimni o'chirish)\n• Anketani yashirish (Do'st topish → 🙈)\n• Botdan chiqib ketish\n\n*Aloqa:* @your_admin_username",
        "terms_text": "📜 *Foydalanish shartlari*\n\n*Botdan foydalanib, siz quyidagi shartlarga rozilik bildirasiz:*\n\n1️⃣ *Yosh chegarasi:* Faqat 18 yoshdan oshgan foydalanuvchilar uchun\n\n2️⃣ *Hurmat:* Hurmatsizlik, tahdid, nomaqbul kontent qat'iyan taqiqlanadi. AI avtomatik aniqlaydi va bloklaydi\n\n3️⃣ *Halollik:* Soxta profil, taqlid, boshqa odamning rasmlaridan foydalanish taqiqlanadi\n\n4️⃣ *AI maslahati:* Bot maslahat beradi, lekin professional psixolog, shifokor yoki advokat o'rnini bosa olmaydi\n\n5️⃣ *Premium:* To'langan obuna pul qaytarilmaydi. Obuna avtomatik yangilanmaydi\n\n6️⃣ *Mas'uliyat:* Bot foydalanuvchilar o'rtasidagi munosabatlar uchun mas'uliyat olmaydi\n\n7️⃣ *O'zgarishlar:* Shartlar yangilanishi mumkin. Sezilarli o'zgarishlar haqida sizga xabar beriladi\n\n*Aloqa:* @your_admin_username",
    },

    "errors": {
        "generic": "❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.",
        "invalid_input": "❌ Noto'g'ri kirish. Qaytadan urinib ko'ring.",
        "database": "❌ Ma'lumotlar bazasi xatosi. Qo'llab-quvvatlash bilan bog'laning.",
        "ai_error": "❌ AI xizmati vaqtincha mavjud emas.",
    },

    "buttons": {
        "back": "⬅️ Orqaga",
        "cancel": "❌ Bekor qilish",
        "confirm": "✅ Tasdiqlash",
        "next": "➡️ Keyingi",
    },
}
