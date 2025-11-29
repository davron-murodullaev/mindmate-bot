WORKOUTS = {
    "uz": {
        "morning": {
            "name": "🌅 Ertalabki mashq (10 daq)",
            "exercises": [
                "1. Cho'zilish - 2 daqiqa",
                "2. Jumping Jacks - 30 ta",
                "3. Squat - 20 ta",
                "4. Push-up - 10 ta",
                "5. Plank - 30 soniya",
                "6. Nafas olish - 1 daqiqa"
            ]
        },
        "energy": {
            "name": "⚡ Energiya oshirish (5 daq)",
            "exercises": [
                "1. Jogging joyida - 1 daqiqa",
                "2. High knees - 30 soniya",
                "3. Burpees - 10 ta",
                "4. Mountain climbers - 30 soniya",
                "5. Chuqur nafas - 1 daqiqa"
            ]
        },
        "relax": {
            "name": "🧘 Bo'shashish (7 daq)",
            "exercises": [
                "1. Bo'yin cho'zilishi - 1 daqiqa",
                "2. Yelka aylantirish - 1 daqiqa",
                "3. Bel cho'zilishi - 2 daqiqa",
                "4. Oyoq cho'zilishi - 2 daqiqa",
                "5. Chuqur nafas - 1 daqiqa"
            ]
        },
        "ask": "💪 Qaysi mashqni tanlaysiz?",
        "btn_morning": "🌅 Ertalabki",
        "btn_energy": "⚡ Energiya",
        "btn_relax": "🧘 Bo'shashish",
        "done": "✅ Mashq bajarildi! Statistikaga qo'shildi.",
        "stats_workouts": "💪 Mashqlar soni"
    },
    "ru": {
        "morning": {
            "name": "🌅 Утренняя зарядка (10 мин)",
            "exercises": [
                "1. Растяжка - 2 минуты",
                "2. Jumping Jacks - 30 раз",
                "3. Приседания - 20 раз",
                "4. Отжимания - 10 раз",
                "5. Планка - 30 секунд",
                "6. Дыхание - 1 минута"
            ]
        },
        "energy": {
            "name": "⚡ Заряд энергии (5 мин)",
            "exercises": [
                "1. Бег на месте - 1 минута",
                "2. High knees - 30 секунд",
                "3. Burpees - 10 раз",
                "4. Mountain climbers - 30 секунд",
                "5. Глубокое дыхание - 1 минута"
            ]
        },
        "relax": {
            "name": "🧘 Расслабление (7 мин)",
            "exercises": [
                "1. Растяжка шеи - 1 минута",
                "2. Вращение плеч - 1 минута",
                "3. Растяжка спины - 2 минуты",
                "4. Растяжка ног - 2 минуты",
                "5. Глубокое дыхание - 1 минута"
            ]
        },
        "ask": "💪 Какую тренировку выберете?",
        "btn_morning": "🌅 Утренняя",
        "btn_energy": "⚡ Энергия",
        "btn_relax": "🧘 Расслабление",
        "done": "✅ Тренировка завершена! Добавлено в статистику.",
        "stats_workouts": "💪 Тренировок"
    },
    "en": {
        "morning": {
            "name": "🌅 Morning Workout (10 min)",
            "exercises": [
                "1. Stretching - 2 minutes",
                "2. Jumping Jacks - 30 reps",
                "3. Squats - 20 reps",
                "4. Push-ups - 10 reps",
                "5. Plank - 30 seconds",
                "6. Breathing - 1 minute"
            ]
        },
        "energy": {
            "name": "⚡ Energy Boost (5 min)",
            "exercises": [
                "1. Jogging in place - 1 minute",
                "2. High knees - 30 seconds",
                "3. Burpees - 10 reps",
                "4. Mountain climbers - 30 seconds",
                "5. Deep breathing - 1 minute"
            ]
        },
        "relax": {
            "name": "🧘 Relaxation (7 min)",
            "exercises": [
                "1. Neck stretch - 1 minute",
                "2. Shoulder rolls - 1 minute",
                "3. Back stretch - 2 minutes",
                "4. Leg stretch - 2 minutes",
                "5. Deep breathing - 1 minute"
            ]
        },
        "ask": "💪 Which workout do you choose?",
        "btn_morning": "🌅 Morning",
        "btn_energy": "⚡ Energy",
        "btn_relax": "🧘 Relax",
        "done": "✅ Workout complete! Added to stats.",
        "stats_workouts": "💪 Workouts"
    }
}

def get_workout_text(lang, workout_type):
    w = WORKOUTS.get(lang, WORKOUTS["en"])
    workout = w.get(workout_type, w["morning"])
    text = f"**{workout['name']}**\n\n"
    text += "\n".join(workout["exercises"])
    text += "\n\n✅ Bajarib bo'lgach, «Tayyor» tugmasini bosing!"
    return text

def get_workout_buttons(lang):
    w = WORKOUTS.get(lang, WORKOUTS["en"])
    return {
        "ask": w["ask"],
        "morning": w["btn_morning"],
        "energy": w["btn_energy"],
        "relax": w["btn_relax"]
    }

def get_workout_done(lang):
    return WORKOUTS.get(lang, WORKOUTS["en"])["done"]

def get_workout_stats_label(lang):
    return WORKOUTS.get(lang, WORKOUTS["en"])["stats_workouts"]