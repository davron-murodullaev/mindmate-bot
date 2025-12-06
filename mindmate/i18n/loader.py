"""
i18n/loader.py - MindMate Multi-Language Translation Loader

This module contains all translations for 13 supported languages:
UZ, RU, EN, TR, AR, HI, ZH, KO, JA, ES, FR, DE, PT
"""

TRANSLATIONS = {
    # ============ O'ZBEK TILI ============
    "uz": {
        "welcome": """
🌟 **Salom! Men MindMate** - sizning shaxsiy AI yordamchingizman.

Men sizga yordam bera olaman:
- 😊 Kayfiyatingizni kuzatish
- 📝 Kundalik yozish
- 🧘 Meditatsiya qilish
- 💬 Suhbatlashish va maslahat olish

Quyidagi tugmalardan birini tanlang yoki shunchaki xabar yozing!
        """,
        "help": "📚 **Yordam**\n\nMen sizning shaxsiy AI yordamchingizman.",
        "main_menu": "🏠 **Bosh Menyu**\n\nBo'limni tanlang:",
        "mood_ask": "Bugun o'zingizni qanday his qilyapsiz?",
        "mood_saved": "Kayfiyat saqlandi!",
        "mood_responses": {
            1: "Tushunaman, og'ir kun bo'lyapti. Men shu yerdaman. Nima qiynayapti?",
            2: "Har kimda bunday kunlar bo'ladi. Gaplashmoqchimisiz?",
            3: "Tushundim. Kayfiyatingizni yaxshilash uchun biror narsa qilaylikmi?",
            4: "Yaxshi! Bugun nima yaxshi bo'ldi?",
            5: "Ajoyib! Sizning baxtingiz meni ham xursand qiladi! 🌟"
        },
        "journal_ask": "📝 **Kundalik**\n\nBugun nima bo'ldi? His-tuyg'ularingizni yozing...",
        "journal_saved": "✅ Kundalik saqlandi!",
        "meditate_ask": "🧘 Qaysi meditatsiyani tanlaysiz?",
        "stats_title": "📊 **Sizning statistikangiz**",
        "reset_done": "🔄 Suhbat yangilandi!",
        "lang_changed": "✅ Til o'zgartirildi!",
        "btn_chat": "💬 Suhbat",
        "btn_healer": "🌿 Shifokor",
        "btn_mood": "😊 Kayfiyat",
        "btn_journal": "📝 Kundalik",
        "btn_meditate": "🧘 Meditatsiya",
        "btn_fitness": "💪 Fitness",
        "btn_reminders": "⏰ Eslatmalar",
        "btn_stats": "📊 Statistika",
        "btn_lang": "🌍 Til",
        "btn_back": "🔙 Orqaga",
        "btn_main_menu": "🏠 Bosh menyu",
        # Menu button labels
        "menu_mood": "😊 Kayfiyat",
        "menu_journal": "📝 Kundalik",
        "menu_meditate": "🧘 Meditatsiya",
        "menu_fitness": "💪 Fitness",
        "menu_healer": "🌿 Shifokor",
        "menu_stats": "📊 Statistika",
        "menu_productivity": "⚡ Samaradorlik",
        "menu_finance": "💰 Moliya",
        # Action labels
        "back": "Orqaga",
        "cancel": "Bekor qilish",
        "yes": "Ha",
        "no": "Yo'q",
        "error": "Kechirasiz, hozir javob bera olmayapman. Keyinroq urinib ko'ring."
    },
    
    # ============ RUS TILI ============
    "ru": {
        "welcome": """
🌟 **Привет! Я MindMate** - ваш личный AI помощник.

Я могу помочь вам:
- 😊 Отслеживать настроение
- 📝 Вести дневник
- 🧘 Медитировать
- 💬 Общаться и получать советы

Выберите кнопку ниже или просто напишите мне!
        """,
        "help": "📚 **Помощь**\n\nЯ ваш личный AI помощник.",
        "main_menu": "🏠 **Главное меню**\n\nВыберите раздел:",
        "mood_ask": "Как вы себя чувствуете сегодня?",
        "mood_saved": "Настроение сохранено!",
        "mood_responses": {
            1: "Понимаю, тяжёлый день. Я здесь. Что беспокоит?",
            2: "У всех бывают такие дни. Хотите поговорить?",
            3: "Понял. Сделаем что-нибудь для улучшения настроения?",
            4: "Хорошо! Что хорошего произошло сегодня?",
            5: "Отлично! Ваше счастье радует и меня! 🌟"
        },
        "journal_ask": "📝 **Дневник**\n\nЧто произошло сегодня? Напишите свои мысли...",
        "journal_saved": "✅ Запись сохранена!",
        "meditate_ask": "🧘 Какую медитацию выберете?",
        "stats_title": "📊 **Ваша статистика**",
        "reset_done": "🔄 Чат сброшен!",
        "lang_changed": "✅ Язык изменён!",
        "btn_chat": "💬 Чат",
        "btn_healer": "🌿 Целитель",
        "btn_mood": "😊 Настроение",
        "btn_journal": "📝 Дневник",
        "btn_meditate": "🧘 Медитация",
        "btn_fitness": "💪 Фитнес",
        "btn_reminders": "⏰ Напоминания",
        "btn_stats": "📊 Статистика",
        "btn_lang": "🌍 Язык",
        "btn_back": "🔙 Назад",
        "btn_main_menu": "🏠 Главное меню",
        # Menu button labels
        "menu_mood": "😊 Настроение",
        "menu_journal": "📝 Дневник",
        "menu_meditate": "🧘 Медитация",
        "menu_fitness": "💪 Фитнес",
        "menu_healer": "🌿 Целитель",
        "menu_stats": "📊 Статистика",
        "menu_productivity": "⚡ Продуктивность",
        "menu_finance": "💰 Финансы",
        # Action labels
        "back": "Назад",
        "cancel": "Отмена",
        "yes": "Да",
        "no": "Нет",
        "error": "Извините, не могу ответить сейчас. Попробуйте позже."
    },
    
    # ============ INGLIZ TILI ============
    "en": {
        "welcome": """
🌟 **Hello! I'm MindMate** - your personal AI assistant.

I can help you with:
- 😊 Tracking your mood
- 📝 Journaling
- 🧘 Meditation
- 💬 Chatting and advice

Choose a button below or just send me a message!
        """,
        "help": "📚 **Help**\n\nI'm your personal AI assistant.",
        "main_menu": "🏠 **Main Menu**\n\nChoose a section:",
        "mood_ask": "How are you feeling today?",
        "mood_saved": "Mood saved!",
        "mood_responses": {
            1: "I understand, it's a tough day. I'm here. What's troubling you?",
            2: "Everyone has days like this. Want to talk?",
            3: "Got it. Shall we do something to improve your mood?",
            4: "Nice! What good happened today?",
            5: "Awesome! Your happiness makes me happy too! 🌟"
        },
        "journal_ask": "📝 **Journal**\n\nWhat happened today? Write your thoughts...",
        "journal_saved": "✅ Journal saved!",
        "meditate_ask": "🧘 Which meditation do you choose?",
        "stats_title": "📊 **Your Statistics**",
        "reset_done": "🔄 Chat reset!",
        "lang_changed": "✅ Language changed!",
        "btn_chat": "💬 Chat",
        "btn_healer": "🌿 Healer",
        "btn_mood": "😊 Mood",
        "btn_journal": "📝 Journal",
        "btn_meditate": "🧘 Meditate",
        "btn_fitness": "💪 Fitness",
        "btn_reminders": "⏰ Reminders",
        "btn_stats": "📊 Stats",
        "btn_lang": "🌍 Language",
        "btn_back": "🔙 Back",
        "btn_main_menu": "🏠 Main Menu",
        # Menu button labels
        "menu_mood": "😊 Mood",
        "menu_journal": "📝 Journal",
        "menu_meditate": "🧘 Meditate",
        "menu_fitness": "💪 Fitness",
        "menu_healer": "🌿 Healer",
        "menu_stats": "📊 Stats",
        "menu_productivity": "⚡ Productivity",
        "menu_finance": "💰 Finance",
        # Action labels
        "back": "Back",
        "cancel": "Cancel",
        "yes": "Yes",
        "no": "No",
        "error": "Sorry, I can't respond right now. Please try later."
    },
    
    # ============ TURK TILI ============
    "tr": {
        "welcome": """
🌟 **Merhaba! Ben MindMate** - kişisel AI asistanınızım.

Size yardımcı olabilirim:
- 😊 Ruh halinizi takip etme
- 📝 Günlük tutma
- 🧘 Meditasyon
- 💬 Sohbet ve tavsiye

Aşağıdaki butonlardan birini seçin veya bana mesaj yazın!
        """,
        "help": "📚 **Yardım**\n\nBen kişisel AI asistanınızım.",
        "main_menu": "🏠 **Ana Menü**\n\nBir bölüm seçin:",
        "mood_ask": "Bugün kendinizi nasıl hissediyorsunuz?",
        "mood_saved": "Ruh hali kaydedildi!",
        "mood_responses": {
            1: "Anlıyorum, zor bir gün. Buradayım. Sizi ne üzüyor?",
            2: "Herkesin böyle günleri olur. Konuşmak ister misiniz?",
            3: "Anladım. Ruh halinizi iyileştirmek için bir şeyler yapalım mı?",
            4: "Güzel! Bugün ne güzel oldu?",
            5: "Harika! Mutluluğunuz beni de mutlu ediyor! 🌟"
        },
        "journal_ask": "📝 **Günlük**\n\nBugün ne oldu? Düşüncelerinizi yazın...",
        "journal_saved": "✅ Günlük kaydedildi!",
        "meditate_ask": "🧘 Hangi meditasyonu seçersiniz?",
        "stats_title": "📊 **İstatistikleriniz**",
        "reset_done": "🔄 Sohbet sıfırlandı!",
        "lang_changed": "✅ Dil değiştirildi!",
        "btn_chat": "💬 Sohbet",
        "btn_healer": "🌿 Şifacı",
        "btn_mood": "😊 Ruh Hali",
        "btn_journal": "📝 Günlük",
        "btn_meditate": "🧘 Meditasyon",
        "btn_fitness": "💪 Fitness",
        "btn_reminders": "⏰ Hatırlatıcılar",
        "btn_stats": "📊 İstatistik",
        "btn_lang": "🌍 Dil",
        "btn_back": "🔙 Geri",
        "btn_main_menu": "🏠 Ana Menü",
        # Menu button labels
        "menu_mood": "😊 Ruh Hali",
        "menu_journal": "📝 Günlük",
        "menu_meditate": "🧘 Meditasyon",
        "menu_fitness": "💪 Fitness",
        "menu_healer": "🌿 Şifacı",
        "menu_stats": "📊 İstatistik",
        "menu_productivity": "⚡ Verimlilik",
        "menu_finance": "💰 Finans",
        # Action labels
        "back": "Geri",
        "cancel": "İptal",
        "yes": "Evet",
        "no": "Hayır",
        "error": "Üzgünüm, şu anda yanıt veremiyorum. Daha sonra deneyin."
    },
    
    # ============ ARAB TILI ============
    "ar": {
        "welcome": """
🌟 **مرحباً! أنا MindMate** - مساعدك الشخصي بالذكاء الاصطناعي.

يمكنني مساعدتك في:
- 😊 تتبع مزاجك
- 📝 كتابة اليوميات
- 🧘 التأمل
- 💬 الدردشة والنصائح

اختر زراً أدناه أو أرسل لي رسالة!
        """,
        "help": "📚 **مساعدة**\n\nأنا مساعدك الشخصي بالذكاء الاصطناعي.",
        "main_menu": "🏠 **القائمة الرئيسية**\n\nاختر قسماً:",
        "mood_ask": "كيف تشعر اليوم؟",
        "mood_saved": "تم حفظ المزاج!",
        "mood_responses": {
            1: "أفهم، يوم صعب. أنا هنا. ما الذي يزعجك؟",
            2: "الجميع لديهم أيام كهذه. هل تريد التحدث؟",
            3: "فهمت. هل نفعل شيئاً لتحسين مزاجك؟",
            4: "جيد! ما الشيء الجيد الذي حدث اليوم؟",
            5: "رائع! سعادتك تسعدني أيضاً! 🌟"
        },
        "journal_ask": "📝 **اليوميات**\n\nماذا حدث اليوم؟ اكتب أفكارك...",
        "journal_saved": "✅ تم حفظ اليوميات!",
        "meditate_ask": "🧘 أي تأمل تختار؟",
        "stats_title": "📊 **إحصائياتك**",
        "reset_done": "🔄 تم إعادة ضبط المحادثة!",
        "lang_changed": "✅ تم تغيير اللغة!",
        "btn_chat": "💬 دردشة",
        "btn_healer": "🌿 معالج",
        "btn_mood": "😊 المزاج",
        "btn_journal": "📝 اليوميات",
        "btn_meditate": "🧘 تأمل",
        "btn_fitness": "💪 لياقة",
        "btn_reminders": "⏰ تذكيرات",
        "btn_stats": "📊 إحصائيات",
        "btn_lang": "🌍 اللغة",
        "btn_back": "🔙 رجوع",
        "btn_main_menu": "🏠 القائمة الرئيسية",
        # Menu button labels
        "menu_mood": "😊 المزاج",
        "menu_journal": "📝 اليوميات",
        "menu_meditate": "🧘 تأمل",
        "menu_fitness": "💪 لياقة",
        "menu_healer": "🌿 معالج",
        "menu_stats": "📊 إحصائيات",
        "menu_productivity": "⚡ إنتاجية",
        "menu_finance": "💰 مالية",
        # Action labels
        "back": "رجوع",
        "cancel": "إلغاء",
        "yes": "نعم",
        "no": "لا",
        "error": "عذراً، لا أستطيع الرد الآن. حاول لاحقاً."
    },
    
    # ============ HIND TILI ============
    "hi": {
        "welcome": """
🌟 **नमस्ते! मैं MindMate हूं** - आपका व्यक्तिगत AI सहायक।

मैं आपकी मदद कर सकता हूं:
- 😊 मूड ट्रैक करना
- 📝 डायरी लिखना
- 🧘 ध्यान करना
- 💬 बातचीत और सलाह

नीचे दिए गए बटन चुनें या मुझे संदेश भेजें!
        """,
        "help": "📚 **सहायता**\n\nमैं आपका व्यक्तिगत AI सहायक हूं।",
        "main_menu": "🏠 **मुख्य मेनू**\n\nएक अनुभाग चुनें:",
        "mood_ask": "आज आप कैसा महसूस कर रहे हैं?",
        "mood_saved": "मूड सहेजा गया!",
        "mood_responses": {
            1: "समझता हूं, मुश्किल दिन है। मैं यहां हूं। क्या परेशान कर रहा है?",
            2: "सभी के ऐसे दिन होते हैं। बात करना चाहते हैं?",
            3: "समझ गया। मूड बेहतर करने के लिए कुछ करें?",
            4: "अच्छा! आज क्या अच्छा हुआ?",
            5: "शानदार! आपकी खुशी मुझे भी खुश करती है! 🌟"
        },
        "journal_ask": "📝 **डायरी**\n\nआज क्या हुआ? अपने विचार लिखें...",
        "journal_saved": "✅ डायरी सहेजी गई!",
        "meditate_ask": "🧘 कौन सा ध्यान चुनेंगे?",
        "stats_title": "📊 **आपके आंकड़े**",
        "reset_done": "🔄 चैट रीसेट हो गई!",
        "lang_changed": "✅ भाषा बदल गई!",
        "btn_chat": "💬 चैट",
        "btn_healer": "🌿 हीलर",
        "btn_mood": "😊 मूड",
        "btn_journal": "📝 डायरी",
        "btn_meditate": "🧘 ध्यान",
        "btn_fitness": "💪 फिटनेस",
        "btn_reminders": "⏰ रिमाइंडर",
        "btn_stats": "📊 आंकड़े",
        "btn_lang": "🌍 भाषा",
        "btn_back": "🔙 वापस",
        "btn_main_menu": "🏠 मुख्य मेनू",
        # Menu button labels
        "menu_mood": "😊 मूड",
        "menu_journal": "📝 डायरी",
        "menu_meditate": "🧘 ध्यान",
        "menu_fitness": "💪 फिटनेस",
        "menu_healer": "🌿 हीलर",
        "menu_stats": "📊 आंकड़े",
        "menu_productivity": "⚡ उत्पादकता",
        "menu_finance": "💰 वित्त",
        # Action labels
        "back": "वापस",
        "cancel": "रद्द करें",
        "yes": "हाँ",
        "no": "नहीं",
        "error": "क्षमा करें, अभी जवाब नहीं दे सकता। बाद में कोशिश करें।"
    },
    
    # ============ XITOY TILI ============
    "zh": {
        "welcome": """
🌟 **你好！我是 MindMate** - 你的个人AI助手。

我可以帮助你：
- 😊 追踪心情
- 📝 写日记
- 🧘 冥想
- 💬 聊天和建议

选择下面的按钮或给我发消息！
        """,
        "help": "📚 **帮助**\n\n我是你的个人AI助手。",
        "main_menu": "🏠 **主菜单**\n\n选择一个部分：",
        "mood_ask": "今天感觉怎么样？",
        "mood_saved": "心情已保存！",
        "mood_responses": {
            1: "我理解，这是艰难的一天。我在这里。什么困扰着你？",
            2: "每个人都有这样的日子。想聊聊吗？",
            3: "明白了。我们做些什么来改善心情？",
            4: "很好！今天有什么好事发生？",
            5: "太棒了！你的快乐也让我快乐！🌟"
        },
        "journal_ask": "📝 **日记**\n\n今天发生了什么？写下你的想法...",
        "journal_saved": "✅ 日记已保存！",
        "meditate_ask": "🧘 选择哪种冥想？",
        "stats_title": "📊 **你的统计**",
        "reset_done": "🔄 聊天已重置！",
        "lang_changed": "✅ 语言已更改！",
        "btn_chat": "💬 聊天",
        "btn_healer": "🌿 治愈师",
        "btn_mood": "😊 心情",
        "btn_journal": "📝 日记",
        "btn_meditate": "🧘 冥想",
        "btn_fitness": "💪 健身",
        "btn_reminders": "⏰ 提醒",
        "btn_stats": "📊 统计",
        "btn_lang": "🌍 语言",
        "btn_back": "🔙 返回",
        "btn_main_menu": "🏠 主菜单",
        # Menu button labels
        "menu_mood": "😊 心情",
        "menu_journal": "📝 日记",
        "menu_meditate": "🧘 冥想",
        "menu_fitness": "💪 健身",
        "menu_healer": "🌿 治愈师",
        "menu_stats": "📊 统计",
        "menu_productivity": "⚡ 生产力",
        "menu_finance": "💰 财务",
        # Action labels
        "back": "返回",
        "cancel": "取消",
        "yes": "是",
        "no": "否",
        "error": "抱歉，现在无法回复。请稍后再试。"
    },
    
    # ============ KOREYS TILI ============
    "ko": {
        "welcome": """
🌟 **안녕하세요! 저는 MindMate입니다** - 당신의 개인 AI 도우미입니다.

도와드릴 수 있는 것:
- 😊 기분 추적
- 📝 일기 쓰기
- 🧘 명상
- 💬 대화와 조언

아래 버튼을 선택하거나 메시지를 보내세요!
        """,
        "help": "📚 **도움말**\n\n저는 당신의 개인 AI 도우미입니다.",
        "main_menu": "🏠 **메인 메뉴**\n\n섹션을 선택하세요:",
        "mood_ask": "오늘 기분이 어떠세요?",
        "mood_saved": "기분이 저장되었습니다!",
        "mood_responses": {
            1: "이해해요, 힘든 하루네요. 제가 여기 있어요. 무엇이 걱정되나요?",
            2: "누구나 이런 날이 있어요. 이야기하고 싶으세요?",
            3: "알겠어요. 기분을 좋게 할 무언가를 해볼까요?",
            4: "좋아요! 오늘 무슨 좋은 일이 있었나요?",
            5: "멋져요! 당신의 행복이 저도 행복하게 해요! 🌟"
        },
        "journal_ask": "📝 **일기**\n\n오늘 무슨 일이 있었나요? 생각을 적어보세요...",
        "journal_saved": "✅ 일기가 저장되었습니다!",
        "meditate_ask": "🧘 어떤 명상을 선택하시겠어요?",
        "stats_title": "📊 **당신의 통계**",
        "reset_done": "🔄 채팅이 초기화되었습니다!",
        "lang_changed": "✅ 언어가 변경되었습니다!",
        "btn_chat": "💬 채팅",
        "btn_healer": "🌿 힐러",
        "btn_mood": "😊 기분",
        "btn_journal": "📝 일기",
        "btn_meditate": "🧘 명상",
        "btn_fitness": "💪 피트니스",
        "btn_reminders": "⏰ 알림",
        "btn_stats": "📊 통계",
        "btn_lang": "🌍 언어",
        "btn_back": "🔙 뒤로",
        "btn_main_menu": "🏠 메인 메뉴",
        # Menu button labels
        "menu_mood": "😊 기분",
        "menu_journal": "📝 일기",
        "menu_meditate": "🧘 명상",
        "menu_fitness": "💪 피트니스",
        "menu_healer": "🌿 힐러",
        "menu_stats": "📊 통계",
        "menu_productivity": "⚡ 생산성",
        "menu_finance": "💰 재무",
        # Action labels
        "back": "뒤로",
        "cancel": "취소",
        "yes": "예",
        "no": "아니요",
        "error": "죄송합니다, 지금은 답변할 수 없습니다. 나중에 다시 시도해주세요."
    },
    
    # ============ YAPON TILI ============
    "ja": {
        "welcome": """
🌟 **こんにちは！MindMateです** - あなたの個人AIアシスタントです。

お手伝いできること：
- 😊 気分の追跡
- 📝 日記を書く
- 🧘 瞑想
- 💬 チャットとアドバイス

下のボタンを選択するか、メッセージを送ってください！
        """,
        "help": "📚 **ヘルプ**\n\n私はあなたの個人AIアシスタントです。",
        "main_menu": "🏠 **メインメニュー**\n\nセクションを選択：",
        "mood_ask": "今日の気分はいかがですか？",
        "mood_saved": "気分が保存されました！",
        "mood_responses": {
            1: "わかります、大変な一日ですね。私はここにいます。何が気になりますか？",
            2: "誰にでもこんな日があります。話したいですか？",
            3: "わかりました。気分を良くするために何かしましょうか？",
            4: "いいですね！今日は何か良いことがありましたか？",
            5: "素晴らしい！あなたの幸せは私も幸せにします！🌟"
        },
        "journal_ask": "📝 **日記**\n\n今日は何がありましたか？思いを書いてください...",
        "journal_saved": "✅ 日記が保存されました！",
        "meditate_ask": "🧘 どの瞑想を選びますか？",
        "stats_title": "📊 **あなたの統計**",
        "reset_done": "🔄 チャットがリセットされました！",
        "lang_changed": "✅ 言語が変更されました！",
        "btn_chat": "💬 チャット",
        "btn_healer": "🌿 ヒーラー",
        "btn_mood": "😊 気分",
        "btn_journal": "📝 日記",
        "btn_meditate": "🧘 瞑想",
        "btn_fitness": "💪 フィットネス",
        "btn_reminders": "⏰ リマインダー",
        "btn_stats": "📊 統計",
        "btn_lang": "🌍 言語",
        "btn_back": "🔙 戻る",
        "btn_main_menu": "🏠 メインメニュー",
        # Menu button labels
        "menu_mood": "😊 気分",
        "menu_journal": "📝 日記",
        "menu_meditate": "🧘 瞑想",
        "menu_fitness": "💪 フィットネス",
        "menu_healer": "🌿 ヒーラー",
        "menu_stats": "📊 統計",
        "menu_productivity": "⚡ 生産性",
        "menu_finance": "💰 財務",
        # Action labels
        "back": "戻る",
        "cancel": "キャンセル",
        "yes": "はい",
        "no": "いいえ",
        "error": "申し訳ありません、今は返信できません。後でもう一度お試しください。"
    },
    
    # ============ ISPAN TILI ============
    "es": {
        "welcome": """
🌟 **¡Hola! Soy MindMate** - tu asistente personal de IA.

Puedo ayudarte con:
- 😊 Seguimiento del estado de ánimo
- 📝 Escribir un diario
- 🧘 Meditación
- 💬 Charlar y consejos

¡Elige un botón abajo o envíame un mensaje!
        """,
        "help": "📚 **Ayuda**\n\nSoy tu asistente personal de IA.",
        "mood_ask": "¿Cómo te sientes hoy?",
        "mood_saved": "¡Estado de ánimo guardado!",
        "mood_responses": {
            1: "Entiendo, es un día difícil. Estoy aquí. ¿Qué te preocupa?",
            2: "Todos tienen días así. ¿Quieres hablar?",
            3: "Entendido. ¿Hacemos algo para mejorar tu ánimo?",
            4: "¡Bien! ¿Qué bueno pasó hoy?",
            5: "¡Genial! ¡Tu felicidad me hace feliz también! 🌟"
        },
        "journal_ask": "📝 **Diario**\n\n¿Qué pasó hoy? Escribe tus pensamientos...",
        "journal_saved": "✅ ¡Diario guardado!",
        "meditate_ask": "🧘 ¿Qué meditación eliges?",
        "stats_title": "📊 **Tus estadísticas**",
        "reset_done": "🔄 ¡Chat reiniciado!",
        "lang_changed": "✅ ¡Idioma cambiado!",
        "btn_mood": "😊 Ánimo",
        "btn_journal": "📝 Diario",
        "btn_meditate": "🧘 Meditar",
        "btn_fitness": "💪 Fitness",
        "btn_healer": "🌿 Sanador",
        "btn_stats": "📊 Stats",
        "btn_back": "🔙 Atrás",
        "btn_main_menu": "🏠 Menú Principal",
        # Menu button labels
        "menu_mood": "😊 Ánimo",
        "menu_journal": "📝 Diario",
        "menu_meditate": "🧘 Meditar",
        "menu_fitness": "💪 Fitness",
        "menu_healer": "🌿 Sanador",
        "menu_stats": "📊 Estadísticas",
        "menu_productivity": "⚡ Productividad",
        "menu_finance": "💰 Finanzas",
        # Action labels
        "back": "Atrás",
        "cancel": "Cancelar",
        "yes": "Sí",
        "no": "No",
        "error": "Lo siento, no puedo responder ahora. Inténtalo más tarde."
    },
    
    # ============ FRANSUZ TILI ============
    "fr": {
        "welcome": """
🌟 **Bonjour! Je suis MindMate** - votre assistant IA personnel.

Je peux vous aider avec:
- 😊 Suivi de l'humeur
- 📝 Écriture de journal
- 🧘 Méditation
- 💬 Discussion et conseils

Choisissez un bouton ci-dessous ou envoyez-moi un message!
        """,
        "help": "📚 **Aide**\n\nJe suis votre assistant IA personnel.",
        "mood_ask": "Comment vous sentez-vous aujourd'hui?",
        "mood_saved": "Humeur enregistrée!",
        "mood_responses": {
            1: "Je comprends, c'est une journée difficile. Je suis là. Qu'est-ce qui vous préoccupe?",
            2: "Tout le monde a des jours comme ça. Voulez-vous en parler?",
            3: "Compris. Faisons quelque chose pour améliorer votre humeur?",
            4: "Bien! Qu'est-ce qui s'est bien passé aujourd'hui?",
            5: "Super! Votre bonheur me rend heureux aussi! 🌟"
        },
        "journal_ask": "📝 **Journal**\n\nQue s'est-il passé aujourd'hui? Écrivez vos pensées...",
        "journal_saved": "✅ Journal enregistré!",
        "meditate_ask": "🧘 Quelle méditation choisissez-vous?",
        "stats_title": "📊 **Vos statistiques**",
        "reset_done": "🔄 Chat réinitialisé!",
        "lang_changed": "✅ Langue changée!",
        "btn_mood": "😊 Humeur",
        "btn_journal": "📝 Journal",
        "btn_meditate": "🧘 Méditer",
        "btn_fitness": "💪 Fitness",
        "btn_healer": "🌿 Guérisseur",
        "btn_stats": "📊 Stats",
        "btn_back": "🔙 Retour",
        "btn_main_menu": "🏠 Menu Principal",
        # Menu button labels
        "menu_mood": "😊 Humeur",
        "menu_journal": "📝 Journal",
        "menu_meditate": "🧘 Méditer",
        "menu_fitness": "💪 Fitness",
        "menu_healer": "🌿 Guérisseur",
        "menu_stats": "📊 Statistiques",
        "menu_productivity": "⚡ Productivité",
        "menu_finance": "💰 Finances",
        # Action labels
        "back": "Retour",
        "cancel": "Annuler",
        "yes": "Oui",
        "no": "Non",
        "error": "Désolé, je ne peux pas répondre maintenant. Réessayez plus tard."
    },
    
    # ============ NEMIS TILI ============
    "de": {
        "welcome": """
🌟 **Hallo! Ich bin MindMate** - dein persönlicher KI-Assistent.

Ich kann dir helfen mit:
- 😊 Stimmungsverfolgung
- 📝 Tagebuch schreiben
- 🧘 Meditation
- 💬 Chatten und Ratschläge

Wähle einen Button unten oder schreibe mir eine Nachricht!
        """,
        "help": "📚 **Hilfe**\n\nIch bin dein persönlicher KI-Assistent.",
        "mood_ask": "Wie fühlst du dich heute?",
        "mood_saved": "Stimmung gespeichert!",
        "mood_responses": {
            1: "Ich verstehe, es ist ein schwerer Tag. Ich bin hier. Was beschäftigt dich?",
            2: "Jeder hat solche Tage. Möchtest du reden?",
            3: "Verstanden. Sollen wir etwas tun, um deine Stimmung zu verbessern?",
            4: "Gut! Was Gutes ist heute passiert?",
            5: "Toll! Dein Glück macht mich auch glücklich! 🌟"
        },
        "journal_ask": "📝 **Tagebuch**\n\nWas ist heute passiert? Schreibe deine Gedanken...",
        "journal_saved": "✅ Tagebuch gespeichert!",
        "meditate_ask": "🧘 Welche Meditation wählst du?",
        "stats_title": "📊 **Deine Statistiken**",
        "reset_done": "🔄 Chat zurückgesetzt!",
        "lang_changed": "✅ Sprache geändert!",
        "btn_mood": "😊 Stimmung",
        "btn_journal": "📝 Tagebuch",
        "btn_meditate": "🧘 Meditieren",
        "btn_fitness": "💪 Fitness",
        "btn_healer": "🌿 Heiler",
        "btn_stats": "📊 Statistik",
        "btn_back": "🔙 Zurück",
        "btn_main_menu": "🏠 Hauptmenü",
        # Menu button labels
        "menu_mood": "😊 Stimmung",
        "menu_journal": "📝 Tagebuch",
        "menu_meditate": "🧘 Meditieren",
        "menu_fitness": "💪 Fitness",
        "menu_healer": "🌿 Heiler",
        "menu_stats": "📊 Statistik",
        "menu_productivity": "⚡ Produktivität",
        "menu_finance": "💰 Finanzen",
        # Action labels
        "back": "Zurück",
        "cancel": "Abbrechen",
        "yes": "Ja",
        "no": "Nein",
        "error": "Entschuldigung, ich kann gerade nicht antworten. Versuche es später."
    },
    
    # ============ PORTUGAL TILI ============
    "pt": {
        "welcome": """
🌟 **Olá! Eu sou o MindMate** - seu assistente pessoal de IA.

Posso ajudar você com:
- 😊 Acompanhamento de humor
- 📝 Escrever diário
- 🧘 Meditação
- 💬 Conversa e conselhos

Escolha um botão abaixo ou me envie uma mensagem!
        """,
        "help": "📚 **Ajuda**\n\nEu sou seu assistente pessoal de IA.",
        "mood_ask": "Como você está se sentindo hoje?",
        "mood_saved": "Humor salvo!",
        "mood_responses": {
            1: "Eu entendo, é um dia difícil. Estou aqui. O que está te preocupando?",
            2: "Todo mundo tem dias assim. Quer conversar?",
            3: "Entendi. Vamos fazer algo para melhorar seu humor?",
            4: "Legal! O que de bom aconteceu hoje?",
            5: "Incrível! Sua felicidade me faz feliz também! 🌟"
        },
        "journal_ask": "📝 **Diário**\n\nO que aconteceu hoje? Escreva seus pensamentos...",
        "journal_saved": "✅ Diário salvo!",
        "meditate_ask": "🧘 Qual meditação você escolhe?",
        "stats_title": "📊 **Suas estatísticas**",
        "reset_done": "🔄 Chat reiniciado!",
        "lang_changed": "✅ Idioma alterado!",
        "btn_mood": "😊 Humor",
        "btn_journal": "📝 Diário",
        "btn_meditate": "🧘 Meditar",
        "btn_fitness": "💪 Fitness",
        "btn_healer": "🌿 Curador",
        "btn_stats": "📊 Stats",
        "btn_back": "🔙 Voltar",
        "btn_main_menu": "🏠 Menu Principal",
        # Menu button labels
        "menu_mood": "😊 Humor",
        "menu_journal": "📝 Diário",
        "menu_meditate": "🧘 Meditar",
        "menu_fitness": "💪 Fitness",
        "menu_healer": "🌿 Curador",
        "menu_stats": "📊 Estatísticas",
        "menu_productivity": "⚡ Produtividade",
        "menu_finance": "💰 Finanças",
        # Action labels
        "back": "Voltar",
        "cancel": "Cancelar",
        "yes": "Sim",
        "no": "Não",
        "error": "Desculpe, não posso responder agora. Tente mais tarde."
    }
}

# Qo'llab-quvvatlanadigan tillar ro'yxati
SUPPORTED_LANGUAGES = {
    "uz": {"name": "O'zbekcha", "flag": "🇺🇿"},
    "ru": {"name": "Русский", "flag": "🇷🇺"},
    "en": {"name": "English", "flag": "🇬🇧"},
    "tr": {"name": "Türkçe", "flag": "🇹🇷"},
    "ar": {"name": "العربية", "flag": "🇸🇦"},
    "hi": {"name": "हिंदी", "flag": "🇮🇳"},
    "zh": {"name": "中文", "flag": "🇨🇳"},
    "ko": {"name": "한국어", "flag": "🇰🇷"},
    "ja": {"name": "日本語", "flag": "🇯🇵"},
    "es": {"name": "Español", "flag": "🇪🇸"},
    "fr": {"name": "Français", "flag": "🇫🇷"},
    "de": {"name": "Deutsch", "flag": "🇩🇪"},
    "pt": {"name": "Português", "flag": "🇵🇹"}
}

def get_text(lang, key):
    """Tarjimani olish"""
    if lang not in TRANSLATIONS:
        lang = "en"
    return TRANSLATIONS.get(lang, {}).get(key, TRANSLATIONS["en"].get(key, key))

def get_mood_response(lang, score):
    """Kayfiyat javobini olish"""
    if lang not in TRANSLATIONS:
        lang = "en"
    return TRANSLATIONS[lang]["mood_responses"].get(score, "")

def get_language_keyboard():
    """Til tanlash klaviaturasi - 2 sahifali"""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    keyboard = [
        [InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz"),
         InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
         InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr"),
         InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar"),
         InlineKeyboardButton("🇮🇳 हिंदी", callback_data="lang_hi")],
        [InlineKeyboardButton("🇨🇳 中文", callback_data="lang_zh"),
         InlineKeyboardButton("🇰🇷 한국어", callback_data="lang_ko"),
         InlineKeyboardButton("🇯🇵 日本語", callback_data="lang_ja")],
        [InlineKeyboardButton("🇪🇸 Español", callback_data="lang_es"),
         InlineKeyboardButton("🇫🇷 Français", callback_data="lang_fr"),
         InlineKeyboardButton("🇩🇪 Deutsch", callback_data="lang_de")],
        [InlineKeyboardButton("🇵🇹 Português", callback_data="lang_pt")],
        [InlineKeyboardButton("🏠 Menu", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)