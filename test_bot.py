#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MindMate Bot Test Suite
Tests all critical functions without requiring database connection
"""

import sys
import os
import io
import pytest

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test if all modules can be imported"""
    from languages import get_text, TRANSLATIONS
    from fitness import get_workout_text, get_workout_buttons
    from healer import get_healer_prompt
    from ai_brain import get_master_prompt

    assert get_text is not None
    assert TRANSLATIONS is not None
    assert get_workout_text is not None
    assert get_workout_buttons is not None
    assert get_healer_prompt is not None
    assert get_master_prompt is not None

    # Test reminders module (may fail without telegram installed)
    try:
        from reminders import get_reminder_text, get_reminder_menu_keyboard
        assert get_reminder_text is not None
        assert get_reminder_menu_keyboard is not None
    except ImportError:
        # Skip if telegram module not installed (acceptable for basic testing)
        pass

def test_language_system():
    """Test language translation system"""
    from languages import get_text, TRANSLATIONS

    # Test supported languages
    languages = ['uz', 'ru', 'en', 'tr', 'ar', 'hi', 'zh', 'ko', 'ja', 'es', 'fr', 'de', 'pt']
    for lang in languages:
        text = get_text(lang, 'welcome')
        assert text, f"Missing translation for {lang}"
        assert len(text) > 0, f"Empty translation for {lang}"

    # Test fallback to English
    unknown_text = get_text('unknown_lang', 'welcome')
    assert unknown_text, "Fallback mechanism failed"
    assert len(unknown_text) > 0, "Empty fallback translation"

def test_ai_prompts():
    """Test AI prompt generation"""
    from ai_brain import get_master_prompt

    # Test prompts for main languages
    for lang in ['uz', 'ru', 'en']:
        prompt = get_master_prompt(lang, "Test memories", "")
        assert prompt, f"No prompt generated for {lang}"
        assert len(prompt) >= 100, f"Prompt too short for {lang}: {len(prompt)} chars"

def test_fitness_module():
    """Test fitness module"""
    from fitness import get_workout_text, get_workout_buttons

    # Test workout types
    workout_types = ['morning', 'energy', 'relax']
    for workout in workout_types:
        for lang in ['uz', 'ru', 'en']:
            text = get_workout_text(lang, workout)
            assert text, f"No workout text for {workout} in {lang}"
            assert len(text) >= 50, f"Workout text too short for {workout} in {lang}"

    # Test buttons
    buttons = get_workout_buttons('uz')
    assert buttons, "No workout buttons returned"
    assert 'morning' in buttons, "Missing 'morning' button"
    assert 'energy' in buttons, "Missing 'energy' button"
    assert 'relax' in buttons, "Missing 'relax' button"

def test_healer_module():
    """Test healer module"""
    from healer import get_healer_prompt

    # Test healer prompts
    for lang in ['uz', 'ru', 'en']:
        prompt = get_healer_prompt(lang)
        assert prompt, f"No healer prompt for {lang}"
        assert len(prompt) >= 100, f"Healer prompt too short for {lang}"

@pytest.mark.skipif(
    True,
    reason="Reminder system requires telegram module - skip for basic testing"
)
def test_reminder_system():
    """Test reminder system"""
    from reminders import get_reminder_text, get_reminder_type_name, get_reminder_emoji

    # Test reminder types
    reminder_types = ['mood', 'meditate', 'workout', 'water']
    for rtype in reminder_types:
        name = get_reminder_type_name(rtype, 'uz')
        emoji = get_reminder_emoji(rtype)
        assert name, f"No reminder name for {rtype}"
        assert emoji, f"No reminder emoji for {rtype}"

    # Test reminder texts
    text_keys = ['reminder_menu', 'set_time', 'reminder_set', 'reminder_deleted']
    for key in text_keys:
        text = get_reminder_text('uz', key)
        assert text, f"Missing reminder text for {key}"

@pytest.mark.skipif(
    not os.path.exists('.env'),
    reason="No .env file found - skipping environment variable check"
)
def test_environment_variables():
    """Test environment variables"""
    from dotenv import load_dotenv

    load_dotenv()

    required_vars = ['TELEGRAM_BOT_TOKEN', 'OPENAI_API_KEY', 'DATABASE_URL']
    missing = []

    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing.append(var)

    assert len(missing) == 0, f"Missing environment variables: {', '.join(missing)}"

if __name__ == "__main__":
    # Run with pytest
    sys.exit(pytest.main([__file__, '-v', '--tb=short']))
