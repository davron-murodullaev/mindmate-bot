"""
English translations
"""

TRANSLATIONS = {
    "welcome": "👋 Welcome to MindMate!\n\nI'm your AI-powered companion for mental health and productivity.\n\nPlease select your language:",

    "setup": {
        "complete": "✅ Setup complete! You can now use all features.",
        "choose_timezone": "Please choose your timezone:",
    },

    "start": {
        "welcome_back": "👋 *Welcome back, {name}!*\n\nWhere shall we start?",
    },

    "menu": {
        "main_menu": "🏠 *Main Menu*\n\nJust type or speak to me — I'll understand.\nOr use the buttons below:",
        "exam": "🎓 Exam",
        "career": "💼 Career",
        "friends": "💝 Find friends",
        "profile": "👤 My Profile",
        "mood_tracking": "😊 Mood",
        "healer": "🌟 Healer",
        "journal": "📝 Journal",
        "productivity": "🎯 Productivity",
        "reminders": "⏰ Reminders",
        "stats": "📊 Statistics",
        "settings": "⚙️ Settings",
        "premium": "💎 Premium",
        "help": "❓ Help",
    },

    "profile": {
        "subtitle": "Pick one of your personal tools below:",
        "exam_view_btn": "🎓 Exam Settings",
        "exam_setup_btn": "🎓 Exam Mentor — Set Up",
        "career_view_btn": "💼 Career Settings",
        "career_setup_btn": "💼 Career Coach — Set Up",
        "friends_view_btn": "💝 Friend Profile",
        "friends_setup_btn": "💝 Find Friends — Set Up",
        "edit_btn": "✏️ Edit",
        "title": "{name}'s Profile",
        "badge_premium": "💎 Premium",
        "badge_free": "🆓 Free",
        "empty_hint": "_Nothing set up yet. Use the buttons below to get started._",
        "exam_not_found": "Exam profile not found.",
        "career_not_found": "Career profile not found.",
        "friends_not_found": "Friend profile not found.",
        "days_left": "{delta} days left",
        "exam_today": "Exam is today! 💪",
        "exam_passed": "passed",
        "no_entry": "not entered",
        "verified": "✅ Verified",
        "pending_verify": "⏳ Pending verification",
        "visible": "👁 Visible",
        "hidden": "🙈 Hidden",
        "exam_detail": {
            "title": "🎓 *Exam Profile*",
            "exam_type": "📌 Exam type",
            "level": "🎯 Level",
            "subjects": "📚 Subjects",
            "date": "📅 Exam date",
            "daily_hours": "⏱ Daily study: {hours} h",
        },
        "career_detail": {
            "title": "💼 *Career Profile*",
            "status": "📊 Status",
            "role": "🎯 Target role",
            "industry": "🏭 Industry",
            "experience": "⏱ Experience: {exp} yr",
            "skills": "🛠 Skills",
        },
        "friends_detail": {
            "title": "💝 *Friend Profile*",
            "name": "👤 Name",
            "age": "🎂 Age",
            "gender": "👥 Gender",
            "city": "📍 City",
            "goal": "🎯 Goal",
            "interests": "🎵 Interests",
            "bio": "📝 Bio",
            "status": "🛡 Status",
        },
    },

    "exam": {
        "teaser": (
            "🎓 *Exam Mentor*\n\n"
            "I'll help you prepare thoroughly for DTM, IELTS or Graduate school:\n\n"
            "🎯 Personal study plan\n"
            "📚 Q&A for every subject\n"
            "🧪 Practice tests\n"
            "💪 Stress management\n\n"
            "Fill in your profile to get started (1 minute)."
        ),
        "start_btn": "✨ Get Started",
        "select_type": "🎓 *Which exam are you preparing for?*",
        "dtm_select_subjects": (
            "📚 *DTM Preparation*\n\n"
            "Which subjects are you taking?\n"
            "Select multiple, then tap *Confirm*."
        ),
        "confirm_btn": "✅ Confirm",
        "min_subject_warn": "Please select at least 1 subject!",
        "select_level": (
            "🎯 What is your current level?\n\n"
            "🌱 Beginner — just starting out\n"
            "🌿 Intermediate — some foundation, need more practice\n"
            "🌳 Advanced — almost ready, aiming for excellence"
        ),
        "date_prompt": (
            "📅 *Exam Date*\n\n"
            "Do you know when your exam is?\n\n"
            "Enter the date like this: `2026-06-15`\n"
            "(Year-Month-Day format)\n\n"
            "Or type `skip` if you don't know yet."
        ),
        "date_past_error": "❌ That date is in the past. Please enter a future date (e.g. `2026-06-15`).",
        "date_format_error": "❌ Invalid date format. Example: `2026-06-15`\n\nOr type `skip`.",
        "setup_done": "✅ *Your profile is ready!*\n\nI'm now your personal exam mentor. Let's get started!",
        "menu": {
            "plan": "📅 Today's Plan",
            "chat": "💬 Q&A",
            "practice": "🧪 Practice Test",
            "stress": "💪 Stress Relief",
            "my_profile": "📊 My Profile",
            "setup": "⚙️ Settings",
        },
        "plan_loading": "⏳ Building your study plan...",
        "plan_error": "Could not generate plan. Please try again.",
        "chat_intro": (
            "💬 *Q&A Mode*\n\n"
            "Ask me anything — about subjects, time management, or exam strategy.\n\n"
            "Examples:\n"
            "• What is the derivative of cosx in trigonometry?\n"
            "• How do I prepare 10 topics in 3 weeks?\n"
            "• What should I do the night before the exam?\n\n"
            "Type /menu to exit"
        ),
        "no_subjects_warn": "Please set up your profile first — add your subjects.",
        "practice_select": "🧪 *Practice Test*\n\nWhich subject do you want a question from?",
        "question_loading": "⏳ Generating question...",
        "question_answer_prompt": "💡 Write your answer — I'll evaluate it.",
        "question_error": "Could not generate question. Please try again.",
        "stress_intro": (
            "💪 *Stress Management*\n\n"
            "How are you feeling as the exam approaches? Tell me — I'll help.\n\n"
            "Examples:\n"
            "• \"I keep forgetting everything\"\n"
            "• \"I'm afraid I'll run out of time\"\n"
            "• \"My parents are putting too much pressure on me\""
        ),
        "dashboard_title": "🎓 *Exam Mentor*",
        "dashboard_prompt": "What shall we work on today?",
        "no_profile": "Please set up your exam profile first. /exam",
        "reset_confirm": "⚙️ *Reset Profile*\n\nThis will delete the old profile and start fresh. Continue?",
        "reset_yes": "✅ Yes, reset",
        "reset_cancel": "❌ Cancel",
        "type": {
            "dtm": "📚 DTM (Uzbek University Exam)",
            "ielts": "🌍 IELTS (English)",
            "sat": "🇺🇸 SAT (International)",
            "magistratura": "🎓 Graduate School",
            "cefr": "📜 CEFR Certificate",
        },
        "level": {
            "beginner": "🌱 Beginner",
            "intermediate": "🌿 Intermediate",
            "advanced": "🌳 Advanced",
        },
        "edit": {
            "title": "🎓 *Edit Exam Profile*",
            "what_to_change": "What would you like to change?",
            "field_type": "📌 Exam Type",
            "field_subjects": "📚 Subjects",
            "field_level": "🎯 Level",
            "field_date": "📅 Exam Date",
            "change_type": "🎓 *Change exam type:*",
            "change_subjects": "📚 *Change subjects:*\n\nSelect subjects, then tap Save.",
            "change_level": "🎯 *Change your level:*",
            "enter_date": "📅 *Enter exam date:*\n\nFormat: `2026-06-15` (Year-Month-Day)\nType `clear` to remove.",
            "save_btn": "✅ Save",
            "date_updated": "✅ Exam date updated!",
            "date_past_error": "❌ Date is in the past. Please enter a future date (`2026-06-15`).",
            "date_format_error": "❌ Invalid format. Example: `2026-06-15`\nOr type `clear` to remove.",
        },
    },

    "career": {
        "teaser": (
            "💼 *Career Coach*\n\n"
            "I'll help you find a great job and grow in your career:\n\n"
            "📝 ATS-friendly resume creation\n"
            "🎤 Interview preparation\n"
            "💰 Salary negotiation techniques\n"
            "📈 6-month career roadmap\n\n"
            "Fill in your profile to get started (1 minute)."
        ),
        "start_btn": "✨ Get Started",
        "select_status": "💼 *What's your current situation?*",
        "enter_role": (
            "🎯 *Target Position*\n\n"
            "What role are you aiming for?\n\n"
            "Examples:\n"
            "• Frontend Developer\n"
            "• HR Manager\n"
            "• Marketing Specialist\n"
            "• Sales Manager\n"
            "• Accountant\n\n"
            "Type it below:"
        ),
        "enter_exp": (
            "⏱ *Years of Experience*\n\n"
            "Enter a number (e.g. `0`, `2`, `5`).\n"
            "Type `0` if you're a student or fresh graduate."
        ),
        "exp_invalid": "❌ Please enter a number between 0 and 60.",
        "setup_done": "✅ *Your profile is ready!*\n\nI'm now your personal career coach. Let's go!",
        "menu": {
            "resume": "📝 Build Resume",
            "review": "🔍 Resume Review",
            "interview": "🎤 Interview Practice",
            "chat": "💬 Get Advice",
            "salary": "💰 Salary Negotiation",
            "plan": "📈 Career Roadmap",
            "my_profile": "⚙️ My Profile",
        },
        "resume_intro": (
            "📝 *Build Resume*\n\n"
            "I'll write your resume! Send me these details *in one message*:\n\n"
            "1️⃣ *Full name, phone, email*\n"
            "2️⃣ *Education* (university, major, year)\n"
            "3️⃣ *Work experience* (company, role, dates, key achievements)\n"
            "4️⃣ *Skills* (technical + languages)\n"
            "5️⃣ *Projects/certifications* (if any)\n\n"
            "Write freely — I'll turn it into a professional resume."
        ),
        "review_intro": (
            "🔍 *Resume Review*\n\n"
            "Paste your current resume below in *full*.\n\n"
            "I'll check:\n"
            "✓ ATS-friendliness (can a robot read it?)\n"
            "✓ Action verbs and numbers\n"
            "✓ Format and structure\n"
            "✓ What needs improvement\n\n"
            "Paste your resume:"
        ),
        "chat_intro": (
            "💬 *Career Advice*\n\n"
            "Ask me anything:\n\n"
            "Examples:\n"
            "• \"With 3 years of experience, how much should I ask for?\"\n"
            "• \"How do I transition into IT?\"\n"
            "• \"How do I improve my LinkedIn profile?\"\n"
            "• \"What's the right way to ask for a raise?\""
        ),
        "salary_intro": (
            "💰 *Salary Negotiation*\n\n"
            "Tell me one of the following:\n\n"
            "1. \"I currently earn X — can I ask for a raise?\"\n"
            "2. \"I got a job offer — how do I negotiate?\"\n"
            "3. \"What's the market rate for my role?\"\n\n"
            "Give specific numbers and context for a precise strategy."
        ),
        "plan_intro": (
            "📈 *6-Month Career Roadmap*\n\n"
            "Tell me: where are you now, and where do you want to be in 6 months?\n\n"
            "Example:\n"
            "_\"I'm a junior frontend developer and want to be mid-level in 6 months\"_\n\n"
            "I'll build a step-by-step plan:\n"
            "• What skills to learn\n"
            "• What projects to build\n"
            "• What courses to take\n"
            "• When to switch jobs\n\n"
            "Tell me:"
        ),
        "dashboard_title": "💼 *Career Coach*",
        "dashboard_prompt": "What shall we work on today?",
        "no_profile": "Please set up your career profile first. /career",
        "reset_confirm": "⚙️ *Reset Profile*\n\nThis will delete the old profile and start fresh. Continue?",
        "reset_yes": "✅ Yes, reset",
        "reset_cancel": "❌ Cancel",
        "interview": {
            "select": "🎤 *Interview Practice*\n\nWhat type of question do you want?",
            "general": "👋 General (HR)",
            "technical": "🛠 Technical",
            "behavioral": "⭐ Behavioral (STAR)",
            "loading": "⏳ Preparing question...",
            "answer_prompt": "💬 Write your answer — I'll give you professional feedback.",
            "error": "Could not generate question.",
            "another": "🎤 Another question",
            "evaluating": "🎯 Evaluating your answer...",
        },
        "resume_loading": "⏳ Writing your resume, please wait...",
        "review_loading": "🔍 Analyzing your resume...",
        "status": {
            "student": "🎓 Student",
            "graduate": "🎯 Graduate (looking for a job)",
            "employed": "💼 Currently employed",
            "switching": "🔄 Switching careers",
            "freelance": "🚀 Freelancer / Business",
        },
        "edit": {
            "title": "💼 *Edit Career Profile*",
            "what_to_change": "What would you like to change?",
            "field_status": "📊 Status",
            "field_role": "🎯 Target Role",
            "field_experience": "⏱ Years of Experience",
            "change_status": "📊 *Change your current status:*",
            "enter_role": "🎯 *Update target role:*\n\nType your new target role:",
            "enter_experience": "⏱ *Update experience:*\n\nHow many years of experience? (number)",
            "role_updated": "✅ Target role updated!",
            "exp_updated": "✅ Experience updated!",
        },
    },

    "voice": {
        "too_large": "🎙 Voice message too large (over 25 MB). Please send a shorter one.",
        "not_understood": "🎙 I couldn't understand your voice message. Please speak more clearly or type instead.",
        "heard": "🎙 _I heard:_ {text}",
        "error": "🎙 Error reading voice message. Please type instead.",
    },

    "general": {
        "cancel_done": "✅ Cancelled.",
    },

    "friends": {
        "teaser": (
            "💝 *Find Friends*\n\n"
            "Meaningful connections — right inside MindMate.\n\n"
            "✨ *Quick profile* — done in a minute\n"
            "🎯 *Smart matching* — by interests and city\n"
            "💬 *Direct Telegram chat* — no separate app\n"
            "🎭 *Three connection types* — friendship, relationship, partnership\n"
            "🔒 *18+ only* — safe community\n"
            "👁 *Your control* — hide your profile anytime\n\n"
            "Fill out your profile and start meeting new people!"
        ),
        "dashboard_title": "💝 *Find Friends*",
        "dashboard_prompt": "_Ready to meet someone new?_",
        "likes_text": "💖 People who liked you: *{count}*",
        "likes_premium_hint": " _(Upgrade to see who)_",
        "verified_badge": "✅ Verified",
        "not_verified_badge": "🔓 Unverified",
        "visibility_active": "👁 Visible",
        "visibility_hidden": "🙈 Hidden",
        "btn_browse": "💝 Start Browsing",
        "btn_myprofile": "✨ My Profile",
        "btn_matches": "💌 Matches",
        "btn_likes": "💖 Who Liked Me",
        "btn_filters": "🎯 Filters",
        "btn_edit": "⚙️ Edit",
        "btn_hide": "🙈 Hide Profile",
        "btn_show": "👁 Show Profile",
        "btn_verified": "✅ Verified",
        "btn_verify_start": "🛡 Verify Profile",
        "btn_pass": "❌ Pass",
        "btn_like": "❤️ Like",
        "btn_block": "🚫 Block",
        "btn_stop_browse": "⏸ Stop Browsing",
        "btn_continue_browse": "➡️ Continue Browsing",
        "btn_write": "💬 Message on Telegram",
        "btn_icebreakers": "💡 Conversation Starters",
        "btn_create": "✨ Create Profile",
        "btn_ai_bio": "✨ Let AI Write My Bio",
        "btn_skip_bio": "⏭ Skip Bio",
        "btn_skip_photos": "⏭ Skip Photos",
        "btn_edit_photos": "📸 Change Photos Only",
        "btn_edit_full": "📝 Rewrite Full Profile",
        "btn_change_photos": "📸 Change Photos",
        "btn_full_edit": "✏️ Full Edit",
        "btn_clear_photos": "🗑 Start Over",
        "btn_confirm_photos": "✅ Confirm ({count}/{max} photos)",
        "btn_gender_male": "👨 Male",
        "btn_gender_female": "👩 Female",
        "btn_gender_any": "🌈 Anyone",
        "btn_get_premium": "💎 Get Premium",
        "btn_start_browsing": "💝 Start Browsing",
        "pref_any": "Anyone",
        "pref_yes": "Yes",
        "pref_no": "No",
        "pref_title": "🎯 *Filters*\n\n_Narrow down who you see while browsing:_",
        "pref_gender_btn": "👤 Gender: {label}",
        "pref_age_btn": "🎂 Age range: {label}",
        "pref_city_btn": "📍 My city only: {label}",
        "pref_gender_title": "👤 *Who are you looking for?*",
        "pref_age_title": "🎂 *Enter age range*\n\nFormat: `min-max`\nExample: `20-30` or `18-100`",
        "pref_age_error": "❌ Invalid format. Example: `20-30` (range 18-100)",
        "pref_age_updated": "✅ Age range updated.",
        "edit_title": "✏️ *Edit Profile*\n\nWhat would you like to change?",
        "wizard_name": "✨ *Create Profile*\n\nFirst, enter your name (your Telegram name or a nickname):",
        "wizard_age": "🎂 *Your age?*\n\nEnter a number (e.g. `22`).\n_This feature is for users {min_age}+._",
        "wizard_looking": "🎯 *What are you looking for?*",
        "wizard_gender": "👤 *Select your gender*\n\n_(Others will find you based on this)_",
        "wizard_city": "🌆 *What city are you in?*\n\nPlease type your city name.\n_Example: London, New York, Tashkent_",
        "wizard_interests": "✨ *Select your interests*\n\nAt least {min}, up to {max}:",
        "wizard_bio": "✨ *Tell us about yourself*\n\n1-3 sentences — who you are and what kind of person you're looking for.\n\n_Maximum {max_len} characters._\n\nOr let AI write it for you:",
        "wizard_photos": "📸 *Add photos to your profile*\n\nYou can send 1 to {max} photos. The first one will be your main photo.\n\n_Send via the gallery icon (not the paperclip)._",
        "wizard_done": "🎉 *Your profile is ready!*\n\nYou can now browse others and they can find you.\n_Tip: verifying your profile gets you 3x more matches._",
        "wizard_ai_bio_loading": "✨ Writing your bio...",
        "wizard_ai_bio_done": "✨ *Your bio:*\n\n_{bio}_\n\n📸 Now send 1 to {max} photos (first photo will be your main one):",
        "wizard_ai_bio_error": "_Couldn't generate bio, continuing without it._",
        "photo_accepted": "✅ {count}/{max} photos received.\n\nYou can send more or confirm:",
        "photo_max_error": "❌ Maximum {max} photos. Tap Confirm or start over.",
        "photo_cleared": "🗑 All cleared.\n\nSend 1 to {max} new photos:",
        "photos_saved": "✅ *{count} photos saved!*",
        "error_save": "❌ Error saving profile. Please try again.",
        "error_photos_save": "❌ Error saving photos. Please try again.",
        "error_doc_convert": "❌ Error processing image. Please send it as a *photo* (camera/gallery icon, not paperclip).",
        "error_moderation": "❌ *I can't accept this photo.*",
        "error_moderation_suffix": "\n\nPlease send a different photo.",
        "validation_name": "❌ Name must be 2-50 characters.",
        "validation_age": "❌ Age must be between {min} and {max}.",
        "validation_gender": "Please select your gender",
        "validation_city": "❌ City name must be 2-100 characters.",
        "validation_interests_min": "Select at least {min} interests!",
        "validation_interests_max": "You can select at most {max}",
        "validation_bio": "❌ Bio is too long ({length} characters). Maximum {max}.",
        "browse_no_profiles": "🔍 *No matching profiles right now*\n\nTry broadening your filters or check back later.",
        "browse_like_quota": "🚫 *Daily like limit reached* ({limit}).\n\n💎 Get *Premium* for unlimited likes!",
        "browse_like_limit_answer": "Daily limit of {limit} likes reached. Get Premium.",
        "browse_blocked_answer": "User blocked",
        "match_text": "🎉 *Match!*\n\nYou and {name} liked each other!\n\n💬 You can message them directly on Telegram or ask AI for conversation starters.",
        "photo_count": "📸 _{count} photos_",
        "icebreakers_title": "💡 *Conversation Starters:*\n\n",
        "icebreakers_loading": "AI is preparing questions...",
        "icebreakers_error": "Technical error.",
        "myprofile_title": "👤 *My Profile:*\n\n",
        "matches_empty": "💌 *Matches*\n\nNo matches yet. Browse profiles to find your match!",
        "matches_title": "💌 *Your matches:*\n",
        "likes_none": "💖 *Who liked you*\n\nNobody yet. Improve your profile and verify your photo to get more matches!",
        "likes_count_free": "💖 *People who liked you: {count}*\n\nUpgrade to 💎 *Premium* to see who they are.",
        "likes_count_premium": "💖 *People who liked you: {count}*\n",
        "likes_later": "_Check back later for updates._",
        "hide_answer": "Profile hidden",
        "show_answer": "Profile visible",
        "verify_no_photo": "❌ Add a photo to your profile first — then you can verify.",
        "verify_intro": "🛡 *Verify Profile*\n\nSend us a *new selfie* — a clear photo of your face in good lighting.\n\nAI will compare it to your profile photo and award you the ✅ *Verified* badge.\n\n_(Verified profiles get 3x more matches.)_",
        "verify_loading": "🔍 AI is verifying...",
        "verify_success": "✅ *Verified!*\n\n_{note}_\n\nYour profile now shows \"✅ Verified\" and you'll get 3x more visibility.",
        "verify_fail": "❌ *Not verified.*\n\n_{note}_\n\nTry again with a clearer selfie in better lighting.",
        "verify_error": "Verification error. Please try again.",
        "verify_no_saved": "❌ Please add a profile photo first.",
        "verified_info": "✅ Your profile is verified! You get 3x more visibility.",
    },

    "mood": {
        "select": "How are you feeling today?",
        "logged": "✅ Mood logged successfully!",
        "happy": "Happy",
        "sad": "Sad",
        "angry": "Angry",
        "anxious": "Anxious",
        "tired": "Tired",
        "excited": "Excited",
        "stats": "📊 Your mood statistics for the past {days} days:",
        "no_data": "No mood data yet. Log your first mood!",
    },

    "healer": {
        "welcome": "🌟 Welcome to Healer Mode\n\nI'm here to listen and provide support. Feel free to share what's on your mind.\n\nType your message below:",
        "active": "🌟 Healer Mode Active\n\nI'm listening. Share your thoughts and feelings:",
        "exit": "Thank you for sharing. Take care of yourself! 💚",
        "crisis": "Your life matters. Please reach out to professional help immediately:\n\n🆘 Crisis Hotlines:\n• 988 (US Suicide & Crisis Lifeline)\n• Text HOME to 741741\n• findahelpline.com (international)\n\nYou are not alone. 💚",
    },

    "journal": {
        "welcome": "📝 Journal\n\nWhat would you like to do?",
        "new_entry": "✍️ New Entry",
        "view_entries": "📖 View Entries",
        "enter_text": "Write your journal entry:\n\n(You can write as much as you'd like)",
        "saved": "✅ Journal entry saved!",
        "no_entries": "You don't have any journal entries yet.",
        "entry": "📝 Entry from {date}:\n\n{content}",
    },

    "productivity": {
        "welcome": "🎯 Productivity Coach\n\nI'm here to help you achieve your goals and boost your productivity!\n\nHow can I help you today?",
        "active": "🎯 Productivity Mode Active\n\nShare your tasks, goals, or ask for productivity advice:",
    },

    "stats": {
        "welcome": "📊 Your Statistics\n\nWhat would you like to see?",
        "mood": "😊 Mood Stats",
        "journal": "📝 Journal Stats",
        "overall": "📈 Overall Stats",
        "summary": "📊 Overall stats ({days} days):\n\n• Mood entries: {moods}\n• Journal entries: {journals}\n• AI conversations: {chats}",
    },

    "reminders": {
        "welcome": "⏰ *Reminders*\n\nI'll remind you on time.",
        "new": "➕ New reminder",
        "list": "📋 My reminders",
        "delete_all": "🗑 Delete all",
        "delete_one": "🗑 Delete",
        "delete_all_confirm": "⚠️ All active reminders will be deleted. Continue?",
        "all_deleted": "✅ All reminders deleted.",
        "deleted": "✅ Reminder deleted.",
        "tap_to_delete": "_Tap a reminder above to delete it._",
        "list_header": "📋 *Your reminders:*",
        "set": "⏰ *Set Reminder*\n\nTell me when and what to remind you about.\n\nExample: _Remind me to drink water at 3pm tomorrow_",
        "created": "✅ *Reminder created!*\n\n📌 _{text}_\n⏰ {time}",
        "notification": "⏰ Reminder: {text}",
        "no_reminders": "📭 You have no active reminders.",
        "list_item": "• {time} — _{text}_",
        "limit_reached": "❌ Free tier allows {limit} reminders max. Upgrade to Premium!",
        "parse_error": "❌ I couldn't parse the time. Please try again.\n\nExample: _Tomorrow at 3pm meeting_",
    },

    "settings": {
        "welcome": "⚙️ Settings",
        "language": "🌐 Language",
        "timezone": "🕐 Timezone",
        "delete_data": "🗑 Delete my data",
        "delete_confirm": "⚠️ All your data will be deleted. Continue?",
        "delete_done": "✅ Your data has been deleted.",
    },

    "premium": {
        "welcome": "💎 Premium Subscription\n\nPremium benefits:\n\n✅ Unlimited AI conversations\n✅ Unlimited reminders\n✅ Deep statistics\n✅ Voice messages\n✅ Priority response\n\nPrice: $2.99/month",
        "subscribe_stars": "⭐ Pay with Telegram Stars (200⭐)",
        "subscribe_card": "💳 Pay with Card",
        "active": "✅ Premium active until: {date}",
        "limit_reached": "❌ Daily free limit reached ({limit} messages). Upgrade to Premium!",
    },

    "payments": {
        "premium_title": "💎 *MindMate Premium*",
        "premium_benefits": "*Premium benefits:*\n✅ Unlimited AI chats\n✅ Unlimited reminders & journal\n✅ Friends: unlimited likes\n✅ See who liked you\n✅ Premium badge (✨)\n✅ Priority responses",
        "select_plan": "*Choose a plan:*",
        "already_premium": "✅ *You already have Premium!*\n\nExpires: *{expires}*\n\nWant to extend? Choose a plan below:",
        "plan_1m_label": "💎 Premium — 1 month",
        "plan_3m_label": "💎 Premium — 3 months",
        "plan_12m_label": "💎 Premium — 12 months",
        "plan_1m_desc": "1-month MindMate Premium",
        "plan_3m_desc": "3-month MindMate Premium (17% off)",
        "plan_12m_desc": "12-month MindMate Premium (33% off)",
        "unknown_plan": "Unknown plan",
        "invoice_error": "❌ Failed to send payment plan. Please try again.",
        "technical_error": "Technical error. Please try again.",
        "generic_error": "❌ An error occurred.",
        "unknown_plan_admin": "❌ Unknown plan. Please contact admin.",
        "success": "🎉 *Premium activated!*\n\n📅 Expires: *{expires}*\n⭐ Paid: *{stars} Stars*\n\nEnjoy unlimited AI chats, unlimited likes, and more. Thank you! 💎",
        "partial_success": "✅ Payment successful, but a minor system error occurred. Contact admin — Premium will be activated manually.",
    },

    "errors": {
        "generic": "❌ Something went wrong. Please try again.",
        "invalid_input": "❌ Invalid input. Please try again.",
        "database": "❌ Database error. Please contact support.",
        "ai_error": "❌ AI service is temporarily unavailable.",
    },

    "buttons": {
        "back": "⬅️ Back",
        "cancel": "❌ Cancel",
        "confirm": "✅ Confirm",
        "next": "➡️ Next",
    },
}
