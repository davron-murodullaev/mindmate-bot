"""
AI Router — the conversational brain.

When a user types or speaks anything (and isn't already in a specific wizard),
this router:
1. Sends the message to the AI with our tool definitions
2. If the AI calls a tool → executes the tool and returns its result
3. If the AI just chats → returns the chat response

This is what makes the bot feel like a real friend — the user doesn't need to
navigate menus; they just say what they want.
"""
import json
import logging
from typing import List, Dict, Any, Optional

from mindmate.ai.tools import TOOLS, TOOL_FUNCTIONS
from mindmate.core.config import settings

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """Sen — MindMate, foydalanuvchining shaxsiy AI yordamchisi va do'sti.

Sening shaxsiyating:
• Samimiy, iliq, lekin professional
• Foydalanuvchini ism bilan chaqirasan (agar bilsang)
• Qisqa va aniq javob berasan (1-3 paragraf)
• O'zbek/rus/ingliz tilida — foydalanuvchi qaysi tilda yozsa, shu tilda javob ber

Sening vazifalaring:
1. Foydalanuvchining xohishini tushun va kerak bo'lsa TOOLS dan foydalan
2. Eslatma qo'shish/o'chirish, kayfiyat saqlash, kundalik yozish — TOOLS orqali
3. Imtihon, karyera, do'st topish so'rasa — open_menu tool orqali yo'naltir
4. Oddiy suhbat — TOOLS chaqirma, oddiy javob ber (do'st kabi)
5. Stress yoki ruhiy yordam kerak bo'lsa — empati va aniq maslahat ber

QILMA:
• Eskimas formal nutq
• Chuqur falsafiy javoblar (qisqa va amaliy)
• Inkor etish — har doim yordam beradigan rejim

QILGIN:
• Foydalanuvchining vaziyatini eslab qol (so'nggi suhbatlardan)
• Kerak bo'lganda tool ishlat — savol bermay, o'zi qil (eslatma yarat va tasdiqla)
• Kerakli bo'lsa proaktiv maslahat ber: "Bu mavzuda Imtihon Mentor yordam beradi, ko'raylikmi?"

MUHIM: tool natijasini foydalanuvchiga ko'rsatish uchun aynan tool qaytargan
matnni ishlat. O'zingdan qo'shimcha matn QO'SHMA agar tool muvaffaqiyatli
bo'lsa.
"""


async def route_message(
    user_id: int,
    message: str,
    history: List[Dict[str, str]],
    lang: str = "uz",
    user_first_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Route a user message through the AI with tool calling.

    Returns a dict with:
        'message' (str): text to send back to user
        'open_menu' (str|None): if AI wants to navigate to a menu
        'tool_called' (str|None): name of tool that was called (for analytics)
    """
    provider = settings.active_provider

    if provider == "openai":
        return await _route_openai(user_id, message, history, lang, user_first_name)
    elif provider == "anthropic":
        return await _route_anthropic(user_id, message, history, lang, user_first_name)
    else:
        return {"message": "AI provayder noto'g'ri sozlangan.", "tool_called": None}


# ──────────────────────── OpenAI ────────────────────────

async def _route_openai(
    user_id: int,
    message: str,
    history: List[Dict[str, str]],
    lang: str,
    user_first_name: Optional[str],
) -> Dict[str, Any]:
    """Route via OpenAI function calling."""
    try:
        # Lazy import so missing dep doesn't break
        from mindmate.ai.core import ai_core
        client = ai_core._client

        name_clause = f"\n\nFoydalanuvchining ismi: {user_first_name}" if user_first_name else ""
        system = SYSTEM_PROMPT + name_clause

        messages: List[Dict[str, Any]] = [{"role": "system", "content": system}]
        for m in history[-12:]:  # Limit history to keep context tight
            role = m.get("role")
            content = m.get("content")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": message})

        response = await client.chat.completions.create(
            model=ai_core.model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0.6,
            max_tokens=ai_core.max_tokens,
        )

        choice = response.choices[0].message

        # Did the AI call a tool?
        if choice.tool_calls:
            tool_call = choice.tool_calls[0]  # Take first one
            fn_name = tool_call.function.name
            try:
                args = json.loads(tool_call.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}

            fn = TOOL_FUNCTIONS.get(fn_name)
            if not fn:
                return {
                    "message": "Texnik xatolik (notanish vosita).",
                    "tool_called": fn_name,
                }

            try:
                result = await fn(user_id=user_id, lang=lang, **args)
            except TypeError as e:
                logger.error(f"Tool argument error for {fn_name}: {e}")
                return {
                    "message": "Iltimos, qaytadan ayting — tushuna olmadim.",
                    "tool_called": fn_name,
                }
            except Exception as e:
                logger.error(f"Tool execution error for {fn_name}: {e}")
                return {
                    "message": "Texnik xatolik. Qayta urinib ko'ring.",
                    "tool_called": fn_name,
                }

            return {
                "message": result.get("message", ""),
                "open_menu": result.get("open_menu"),
                "tool_called": fn_name,
            }

        # Plain chat response
        return {
            "message": choice.content or "...",
            "tool_called": None,
        }

    except Exception as e:
        logger.error(f"OpenAI router error: {e}")
        return {
            "message": (
                "Hozir javob bera olmayapman, tarmoqda muammo bor. "
                "Bir oz kutib qaytadan urinib ko'ring."
            ),
            "tool_called": None,
        }


# ──────────────────────── Anthropic ────────────────────────

async def _route_anthropic(
    user_id: int,
    message: str,
    history: List[Dict[str, str]],
    lang: str,
    user_first_name: Optional[str],
) -> Dict[str, Any]:
    """Route via Anthropic tool use (similar to OpenAI but different syntax)."""
    try:
        from mindmate.ai.core import ai_core
        client = ai_core._client

        # Convert OpenAI tool definitions to Anthropic format
        anthropic_tools = []
        for t in TOOLS:
            fn = t["function"]
            anthropic_tools.append({
                "name": fn["name"],
                "description": fn["description"],
                "input_schema": fn["parameters"],
            })

        name_clause = f"\n\nFoydalanuvchining ismi: {user_first_name}" if user_first_name else ""
        system = SYSTEM_PROMPT + name_clause

        messages = []
        for m in history[-12:]:
            role = m.get("role")
            content = m.get("content")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": message})

        response = await client.messages.create(
            model=ai_core.model,
            system=system,
            messages=messages,
            tools=anthropic_tools,
            max_tokens=ai_core.max_tokens,
            temperature=0.6,
        )

        # Find tool_use block (if any)
        for block in response.content:
            if getattr(block, "type", None) == "tool_use":
                fn_name = block.name
                args = block.input or {}
                fn = TOOL_FUNCTIONS.get(fn_name)
                if not fn:
                    return {"message": "Texnik xatolik.", "tool_called": fn_name}
                try:
                    result = await fn(user_id=user_id, lang=lang, **args)
                except Exception as e:
                    logger.error(f"Tool exec error {fn_name}: {e}")
                    return {"message": "Texnik xatolik.", "tool_called": fn_name}
                return {
                    "message": result.get("message", ""),
                    "open_menu": result.get("open_menu"),
                    "tool_called": fn_name,
                }

        # Plain text response
        for block in response.content:
            if getattr(block, "type", None) == "text":
                return {"message": block.text, "tool_called": None}

        return {"message": "...", "tool_called": None}

    except Exception as e:
        logger.error(f"Anthropic router error: {e}")
        return {
            "message": "Hozir javob bera olmayapman, qayta urining.",
            "tool_called": None,
        }
