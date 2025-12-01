#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MindMate Bot Test Suite
Tests all critical functions without requiring database connection
"""

import sys
import os
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test if all modules can be imported"""
    print("🧪 Testing imports...")
    try:
        from languages import get_text, TRANSLATIONS
        from fitness import get_workout_text, get_workout_buttons
        from healer import get_healer_prompt
        from ai_brain import get_master_prompt
        from reminders import get_reminder_text, get_reminder_menu_keyboard
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_language_system():
    """Test language translation system"""
    print("\n🧪 Testing language system...")
    try:
        from languages import get_text, TRANSLATIONS

        # Test supported languages
        languages = ['uz', 'ru', 'en', 'tr', 'ar', 'hi', 'zh', 'ko', 'ja', 'es', 'fr', 'de', 'pt']
        for lang in languages:
            text = get_text(lang, 'welcome')
            if not text:
                print(f"❌ Missing translation for {lang}")
                return False

        # Test fallback to English
        unknown_text = get_text('unknown_lang', 'welcome')
        if not unknown_text:
            print("❌ Fallback mechanism failed")
            return False

        print(f"✅ Language system working ({len(languages)} languages)")
        return True
    except Exception as e:
        print(f"❌ Language system error: {e}")
        return False

def test_ai_prompts():
    """Test AI prompt generation"""
    print("\n🧪 Testing AI prompts...")
    try:
        from ai_brain import get_master_prompt

        # Test prompts for main languages
        for lang in ['uz', 'ru', 'en']:
            prompt = get_master_prompt(lang, "Test memories", "")
            if not prompt or len(prompt) < 100:
                print(f"❌ Invalid prompt for {lang}")
                return False

        print("✅ AI prompts working")
        return True
    except Exception as e:
        print(f"❌ AI prompt error: {e}")
        return False

def test_fitness_module():
    """Test fitness module"""
    print("\n🧪 Testing fitness module...")
    try:
        from fitness import get_workout_text, get_workout_buttons

        # Test workout types
        workout_types = ['morning', 'energy', 'relax']
        for workout in workout_types:
            for lang in ['uz', 'ru', 'en']:
                text = get_workout_text(lang, workout)
                if not text or len(text) < 50:
                    print(f"❌ Invalid workout text for {workout} in {lang}")
                    return False

        # Test buttons
        buttons = get_workout_buttons('uz')
        if not buttons or 'morning' not in buttons:
            print("❌ Invalid workout buttons")
            return False

        print("✅ Fitness module working")
        return True
    except Exception as e:
        print(f"❌ Fitness module error: {e}")
        return False

def test_healer_module():
    """Test healer module"""
    print("\n🧪 Testing healer module...")
    try:
        from healer import get_healer_prompt

        # Test healer prompts
        for lang in ['uz', 'ru', 'en']:
            prompt = get_healer_prompt(lang)
            if not prompt or len(prompt) < 100:
                print(f"❌ Invalid healer prompt for {lang}")
                return False

        print("✅ Healer module working")
        return True
    except Exception as e:
        print(f"❌ Healer module error: {e}")
        return False

def test_reminder_system():
    """Test reminder system"""
    print("\n🧪 Testing reminder system...")
    try:
        from reminders import get_reminder_text, get_reminder_type_name, get_reminder_emoji

        # Test reminder types
        reminder_types = ['mood', 'meditate', 'workout', 'water']
        for rtype in reminder_types:
            name = get_reminder_type_name(rtype, 'uz')
            emoji = get_reminder_emoji(rtype)
            if not name or not emoji:
                print(f"❌ Invalid reminder data for {rtype}")
                return False

        # Test reminder texts
        text_keys = ['reminder_menu', 'set_time', 'reminder_set', 'reminder_deleted']
        for key in text_keys:
            text = get_reminder_text('uz', key)
            if not text:
                print(f"❌ Missing reminder text for {key}")
                return False

        print("✅ Reminder system working")
        return True
    except Exception as e:
        print(f"❌ Reminder system error: {e}")
        return False

def test_environment_variables():
    """Test environment variables"""
    print("\n🧪 Testing environment variables...")
    try:
        from dotenv import load_dotenv
        import os

        load_dotenv()

        required_vars = ['TELEGRAM_BOT_TOKEN', 'OPENAI_API_KEY', 'DATABASE_URL']
        missing = []

        for var in required_vars:
            value = os.getenv(var)
            if not value:
                missing.append(var)

        if missing:
            print(f"⚠️  Missing environment variables: {', '.join(missing)}")
            print("   Make sure to set them before running the bot!")
            return True  # Not a critical failure for testing

        print("✅ All environment variables set")
        return True
    except Exception as e:
        print(f"❌ Environment error: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("🚀 MindMate Bot - Test Suite")
    print("=" * 60)

    tests = [
        test_imports,
        test_language_system,
        test_ai_prompts,
        test_fitness_module,
        test_healer_module,
        test_reminder_system,
        test_environment_variables
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    print("=" * 60)

    if failed == 0:
        print("✅ All tests passed! Bot is ready to run.")
        return 0
    else:
        print(f"❌ {failed} test(s) failed. Please fix the issues.")
        return 1

if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
