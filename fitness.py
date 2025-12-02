WORKOUTS = {
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

def get_workout_text(lang, workout_type):
    """Get workout text (English only)"""
    workout = WORKOUTS.get(workout_type, WORKOUTS["morning"])
    text = f"**{workout['name']}**\n\n"
    text += "\n".join(workout["exercises"])
    return text

def get_workout_buttons(lang):
    """Get workout button labels (English only)"""
    return {
        "ask": WORKOUTS["ask"],
        "morning": WORKOUTS["btn_morning"],
        "energy": WORKOUTS["btn_energy"],
        "relax": WORKOUTS["btn_relax"]
    }

def get_workout_done(lang):
    """Get workout completion message (English only)"""
    return WORKOUTS["done"]

def get_workout_stats_label(lang):
    """Get workout stats label (English only)"""
    return WORKOUTS["stats_workouts"]
