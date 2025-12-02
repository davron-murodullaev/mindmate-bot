"""
MindMate AI Tools
AI-powered tools: rasm yaratish, tarjima, kod yozish va boshqalar
"""

import logging
from openai import OpenAI
import os

logger = logging.getLogger(__name__)

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Claude API client for code generation
try:
    from anthropic import Anthropic
    claude_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False
    logger.warning("Anthropic library not installed. Code generation will use OpenAI.")
except Exception as e:
    CLAUDE_AVAILABLE = False
    logger.warning(f"Claude API not available: {e}")


# === IMAGE GENERATION ===

async def generate_image(prompt, size="1024x1024"):
    """
    DALL-E orqali rasm yaratish

    Args:
        prompt: Rasm tavsifi
        size: Rasm o'lchami (1024x1024, 512x512, 256x256)

    Returns:
        Image URL yoki None
    """
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality="standard",
            n=1,
        )
        return response.data[0].url
    except Exception as e:
        logger.error(f"Rasm yaratishda xato: {e}")
        # Try DALL-E 2 as fallback
        try:
            response = client.images.generate(
                model="dall-e-2",
                prompt=prompt,
                size="512x512",
                n=1,
            )
            return response.data[0].url
        except Exception as e2:
            logger.error(f"DALL-E 2 fallback ham ishlamadi: {e2}")
            return None


# === TRANSLATION ===

async def translate_text(text, target_lang, source_lang="auto"):
    """
    Matnni tarjima qilish

    Args:
        text: Tarjima qilinadigan matn
        target_lang: Maqsadli til
        source_lang: Manba til (auto - avtomatik aniqlash)

    Returns:
        Tarjima qilingan matn
    """
    try:
        lang_names = {
            "uz": "Uzbek",
            "en": "English",
            "ru": "Russian",
            "tr": "Turkish",
            "ar": "Arabic",
            "zh": "Chinese",
            "es": "Spanish",
            "fr": "French",
            "de": "German"
        }

        target_language = lang_names.get(target_lang, target_lang)

        prompt = f"Translate the following text to {target_language}. Only provide the translation, nothing else:\n\n{text}"

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.3
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.error(f"Tarjima qilishda xato: {e}")
        return None


# === CODE GENERATION ===

async def generate_code(description, language="python"):
    """
    Kod yaratish - Claude API orqali (agar mavjud bo'lsa)

    Args:
        description: Kod tavsifi
        language: Dasturlash tili

    Returns:
        Yaratilgan kod
    """
    try:
        prompt = f"""Write {language} code for the following task:
{description}

Provide clean, well-commented, production-ready code with:
1. Proper error handling
2. Type hints (if applicable)
3. Clear variable names
4. Brief explanation of the approach
5. Example usage"""

        # Use Claude API if available (better for code generation)
        if CLAUDE_AVAILABLE:
            try:
                response = claude_client.messages.create(
                    model="claude-3-5-sonnet-20241022",  # Latest Claude model
                    max_tokens=2048,
                    temperature=0.3,  # Lower temperature for more precise code
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                )

                code_output = response.content[0].text
                return f"🤖 **Generated with Claude AI (Premium Code Generation)**\n\n{code_output}"

            except Exception as claude_error:
                logger.warning(f"Claude API failed, falling back to OpenAI: {claude_error}")
                # Fall through to OpenAI

        # Fallback to OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Use GPT-4 mini for better code quality
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.5
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Kod yaratishda xato: {e}")
        return None


# === RECIPE FINDER ===

async def find_recipe(dish_name, lang="uz"):
    """
    Retsept topish

    Args:
        dish_name: Taom nomi
        lang: Til

    Returns:
        Retsept matni
    """
    try:
        lang_instruction = {
            "uz": "O'zbek tilida",
            "en": "in English",
            "ru": "на русском языке"
        }.get(lang, "in Uzbek")

        prompt = f"""Provide a detailed recipe for {dish_name} {lang_instruction}.
Include:
1. Ingredients with amounts
2. Step-by-step instructions
3. Cooking time
4. Serving size
5. Pro tips

Format it nicely with emojis."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1200,
            temperature=0.7
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Retsept topishda xato: {e}")
        return None


# === TRAVEL PLANNER ===

async def create_travel_plan(destination, duration, budget=None, lang="uz"):
    """
    Sayohat rejasi yaratish

    Args:
        destination: Manzil
        duration: Davomiylik (kun)
        budget: Byudjet
        lang: Til

    Returns:
        Sayohat rejasi
    """
    try:
        lang_instruction = {
            "uz": "O'zbek tilida",
            "en": "in English",
            "ru": "на русском языке"
        }.get(lang, "in Uzbek")

        budget_text = f" with a budget of {budget}" if budget else ""

        prompt = f"""Create a detailed {duration}-day travel plan for {destination}{budget_text} {lang_instruction}.

Include:
1. Day-by-day itinerary
2. Must-see attractions
3. Local food recommendations
4. Transportation tips
5. Accommodation suggestions
6. Budget breakdown (if budget provided)
7. Useful phrases
8. Safety tips

Format nicely with emojis and sections."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.7
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Sayohat rejasi yaratishda xato: {e}")
        return None


# === STUDY MATERIALS ===

async def create_study_material(topic, level="beginner", lang="uz"):
    """
    O'quv materiali yaratish

    Args:
        topic: Mavzu
        level: Daraja (beginner, intermediate, advanced)
        lang: Til

    Returns:
        O'quv materiali
    """
    try:
        lang_instruction = {
            "uz": "O'zbek tilida",
            "en": "in English",
            "ru": "на русском языке"
        }.get(lang, "in Uzbek")

        prompt = f"""Create comprehensive study material about {topic} for {level} level {lang_instruction}.

Include:
1. Introduction and overview
2. Key concepts explained simply
3. Examples and use cases
4. Practice exercises (5-10 questions)
5. Tips for mastery
6. Additional resources

Format with clear sections and emojis."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.6
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"O'quv materiali yaratishda xato: {e}")
        return None


# === TEXT SUMMARIZATION ===

async def summarize_text(text, lang="uz"):
    """
    Matnni qisqartirish

    Args:
        text: Qisqartirilishi kerak bo'lgan matn
        lang: Til

    Returns:
        Qisqartirilgan matn
    """
    try:
        lang_instruction = {
            "uz": "O'zbek tilida",
            "en": "in English",
            "ru": "на русском языке"
        }.get(lang, "in Uzbek")

        prompt = f"""Summarize the following text {lang_instruction}. Provide key points in bullet format:

{text}"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.5
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Matn qisqartirishda xato: {e}")
        return None


# === BUSINESS IDEA GENERATOR ===

async def generate_business_idea(industry=None, lang="uz"):
    """
    Biznes g'oyasi yaratish

    Args:
        industry: Soha (ixtiyoriy)
        lang: Til

    Returns:
        Biznes g'oyasi tavsifi
    """
    try:
        lang_instruction = {
            "uz": "O'zbek tilida",
            "en": "in English",
            "ru": "на русском языке"
        }.get(lang, "in Uzbek")

        industry_text = f" in the {industry} industry" if industry else ""

        prompt = f"""Generate an innovative business idea{industry_text} {lang_instruction}.

Include:
1. Business concept
2. Target market
3. Unique value proposition
4. Revenue model
5. Initial steps to start
6. Potential challenges
7. Growth opportunities

Be creative and practical!"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.9
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Biznes g'oyasi yaratishda xato: {e}")
        return None


# === EMAIL WRITER ===

async def write_email(purpose, recipient_type, key_points, lang="uz"):
    """
    Email yozish

    Args:
        purpose: Maqsad (job application, complaint, inquiry, etc.)
        recipient_type: Qabul qiluvchi (boss, customer, friend, etc.)
        key_points: Asosiy fikrlar
        lang: Til

    Returns:
        Tayyor email
    """
    try:
        lang_instruction = {
            "uz": "O'zbek tilida",
            "en": "in English",
            "ru": "на русском языке"
        }.get(lang, "in Uzbek")

        prompt = f"""Write a professional email {lang_instruction}:

Purpose: {purpose}
Recipient: {recipient_type}
Key points to include: {key_points}

Make it polite, clear, and professional."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.6
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Email yozishda xato: {e}")
        return None


# === LANGUAGE TEXTS ===

def get_ai_tools_text(lang="uz"):
    """AI tools uchun tarjimalar"""
    return {
        "uz": {
            "image_prompt": "🎨 Qanday rasm yaratishni xohlaysiz? Batafsil tasvirlang:",
            "image_generating": "🎨 Rasm yaratilmoqda... Kuting...",
            "image_ready": "✅ Rasm tayyor!",
            "translate_prompt": "🌐 Tarjima qilmoqchi bo'lgan matnni yuboring:",
            "translate_lang": "🌍 Qaysi tilga tarjima qilish kerak?",
            "code_prompt": "👨‍💻 Qanday kod yozish kerak? Batafsil yozing:",
            "code_lang": "💻 Qaysi dasturlash tili? (python/javascript/java/c++)",
            "recipe_prompt": "🍳 Qaysi taom retseptini qidiramiz?",
            "travel_dest": "✈️ Qayerga sayohat qilmoqchisiz?",
            "travel_days": "📅 Necha kunlik sayohat?",
            "study_topic": "📚 Qaysi mavzuni o'rganmoqchisiz?",
            "business_industry": "💼 Qaysi sohada biznes g'oyasi kerak? (ixtiyoriy)",
            "menu_title": "🤖 **AI Yordamchilar**\n\nQaysi vosita kerak?",
            "error": "⚠️ Xatolik yuz berdi. Qaytadan urinib ko'ring.",
        },
        "en": {
            "image_prompt": "🎨 What image would you like to create? Describe in detail:",
            "image_generating": "🎨 Generating image... Please wait...",
            "image_ready": "✅ Image ready!",
            "translate_prompt": "🌐 Send the text you want to translate:",
            "translate_lang": "🌍 Which language to translate to?",
            "code_prompt": "👨‍💻 What code do you need? Describe in detail:",
            "code_lang": "💻 Which programming language? (python/javascript/java/c++)",
            "recipe_prompt": "🍳 Which recipe are we looking for?",
            "travel_dest": "✈️ Where do you want to travel?",
            "travel_days": "📅 How many days?",
            "study_topic": "📚 What topic do you want to study?",
            "business_industry": "💼 Which industry for business idea? (optional)",
            "menu_title": "🤖 **AI Tools**\n\nWhich tool do you need?",
            "error": "⚠️ An error occurred. Please try again.",
        },
        "ru": {
            "image_prompt": "🎨 Какое изображение вы хотите создать? Опишите подробно:",
            "image_generating": "🎨 Создаю изображение... Подождите...",
            "image_ready": "✅ Изображение готово!",
            "translate_prompt": "🌐 Отправьте текст для перевода:",
            "translate_lang": "🌍 На какой язык перевести?",
            "code_prompt": "👨‍💻 Какой код нужен? Опишите подробно:",
            "code_lang": "💻 Какой язык программирования? (python/javascript/java/c++)",
            "recipe_prompt": "🍳 Какой рецепт ищем?",
            "travel_dest": "✈️ Куда хотите поехать?",
            "travel_days": "📅 Сколько дней?",
            "study_topic": "📚 Какую тему хотите изучить?",
            "business_industry": "💼 В какой сфере нужна бизнес-идея? (по желанию)",
            "menu_title": "🤖 **AI Инструменты**\n\nКакой инструмент нужен?",
            "error": "⚠️ Произошла ошибка. Попробуйте еще раз.",
        }
    }.get(lang, {})
