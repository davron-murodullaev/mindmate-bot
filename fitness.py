WORKOUTS = {
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
    },
    "ru": {
        "morning": {
            "name": "🌅 Утренняя тренировка (10 мин)",
            "exercises": [
                "1. Растяжка - 2 минуты",
                "2. Jumping Jacks - 30 повторов",
                "3. Приседания - 20 повторов",
                "4. Отжимания - 10 повторов",
                "5. Планка - 30 секунд",
                "6. Дыхание - 1 минута"
            ]
        },
        "energy": {
            "name": "⚡ Энергия (5 мин)",
            "exercises": [
                "1. Бег на месте - 1 минута",
                "2. Высокие колени - 30 секунд",
                "3. Бёрпи - 10 повторов",
                "4. Скалолаз - 30 секунд",
                "5. Глубокое дыхание - 1 минута"
            ]
        },
        "relax": {
            "name": "🧘 Релаксация (7 мин)",
            "exercises": [
                "1. Растяжка шеи - 1 минута",
                "2. Вращение плеч - 1 минута",
                "3. Растяжка спины - 2 минуты",
                "4. Растяжка ног - 2 минуты",
                "5. Глубокое дыхание - 1 минута"
            ]
        },
        "ask": "💪 Какую тренировку выберешь?",
        "btn_morning": "🌅 Утро",
        "btn_energy": "⚡ Энергия",
        "btn_relax": "🧘 Релакс",
        "done": "✅ Тренировка завершена! Добавлено в статистику.",
        "stats_workouts": "💪 Тренировки"
    }
}

def get_workout_text(lang, workout_type):
    """Get workout text with language support"""
    lang_data = WORKOUTS.get(lang, WORKOUTS["en"])
    workout = lang_data.get(workout_type, lang_data["morning"])
    text = f"**{workout['name']}**\n\n"
    text += "\n".join(workout["exercises"])
    return text

def get_workout_buttons(lang):
    """Get workout button labels with language support"""
    lang_data = WORKOUTS.get(lang, WORKOUTS["en"])
    return {
        "ask": lang_data["ask"],
        "morning": lang_data["btn_morning"],
        "energy": lang_data["btn_energy"],
        "relax": lang_data["btn_relax"]
    }

def get_workout_done(lang):
    """Get workout completion message with language support"""
    lang_data = WORKOUTS.get(lang, WORKOUTS["en"])
    return lang_data["done"]

def get_workout_stats_label(lang):
    """Get workout stats label with language support"""
    lang_data = WORKOUTS.get(lang, WORKOUTS["en"])
    return lang_data["stats_workouts"]
