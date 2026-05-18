"""
Core AI functionality — supports OpenAI (ChatGPT) and Anthropic (Claude).

Switch providers via the AI_PROVIDER env var ("openai" or "anthropic").
The handler/engine code never changes — only this file knows the provider.
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional

_RETRY_DELAYS = (1, 2)  # 3 total attempts

from mindmate.core.config import settings

logger = logging.getLogger(__name__)


class AICore:
    """Unified AI interface for OpenAI and Anthropic."""

    def __init__(self):
        self.provider = settings.active_provider
        self.model = settings.active_model
        self.max_tokens = settings.MAX_TOKENS
        self.temperature = settings.TEMPERATURE

        if self.provider == "anthropic":
            import anthropic
            if not settings.ANTHROPIC_API_KEY:
                raise RuntimeError(
                    "AI_PROVIDER=anthropic but ANTHROPIC_API_KEY is empty. "
                    "Set the env var or switch AI_PROVIDER to openai."
                )
            self._client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            logger.info(f"AI provider: Anthropic (model={self.model})")

        elif self.provider == "openai":
            import openai
            if not settings.OPENAI_API_KEY:
                raise RuntimeError(
                    "AI_PROVIDER=openai but OPENAI_API_KEY is empty. "
                    "Set the env var or switch AI_PROVIDER to anthropic."
                )
            self._client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info(f"AI provider: OpenAI (model={self.model})")

        else:
            raise RuntimeError(
                f"Unknown AI_PROVIDER: {self.provider!r} — must be 'openai' or 'anthropic'."
            )

    # ─────────────────────────────────────────────────────────────────
    # Public API (provider-agnostic)
    # ─────────────────────────────────────────────────────────────────

    async def generate_response(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate a response with automatic retry on transient failures."""
        last_exc: Exception = RuntimeError("unreachable")
        for delay in (0, *_RETRY_DELAYS):
            if delay:
                await asyncio.sleep(delay)
            try:
                if self.provider == "anthropic":
                    return await self._generate_anthropic(
                        system_prompt, user_message, conversation_history,
                        temperature, max_tokens,
                    )
                return await self._generate_openai(
                    system_prompt, user_message, conversation_history,
                    temperature, max_tokens,
                )
            except Exception as exc:
                last_exc = exc
                logger.warning("generate_response failed (retrying): %s", exc)
        logger.error(f"generate_response gave up after retries ({self.provider}): {last_exc}")
        return "Texnik xatolik. Qaytadan urinib ko'ring."

    # ─────────────────────────────────────────────────────────────────
    # Anthropic (Claude)
    # ─────────────────────────────────────────────────────────────────

    async def _generate_anthropic(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]],
        temperature: Optional[float],
        max_tokens: Optional[int],
    ) -> str:
        messages: List[Dict[str, str]] = []
        if conversation_history:
            for msg in conversation_history:
                role = msg.get("role")
                content = msg.get("content")
                if role in ("user", "assistant") and content:
                    messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": user_message})

        response = await self._client.messages.create(
            model=self.model,
            max_tokens=max_tokens or self.max_tokens,
            temperature=temperature if temperature is not None else self.temperature,
            system=system_prompt,
            messages=messages,
        )
        if response.content and len(response.content) > 0:
            return response.content[0].text
        return "I'm having trouble generating a response. Please try again."

    # ─────────────────────────────────────────────────────────────────
    # OpenAI (ChatGPT)
    # ─────────────────────────────────────────────────────────────────

    async def _generate_openai(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]],
        temperature: Optional[float],
        max_tokens: Optional[int],
    ) -> str:
        # OpenAI takes the system prompt as the first message
        messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]
        if conversation_history:
            for msg in conversation_history:
                role = msg.get("role")
                content = msg.get("content")
                if role in ("user", "assistant") and content:
                    messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": user_message})

        response = await self._client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens or self.max_tokens,
            temperature=temperature if temperature is not None else self.temperature,
            messages=messages,
        )
        if response.choices and response.choices[0].message:
            return response.choices[0].message.content or ""
        return "I'm having trouble generating a response. Please try again."


# Single global instance
ai_core = AICore()
