"""
Core AI functionality using Anthropic Claude
"""
import anthropic
from typing import List, Dict, Any, Optional
import logging
import asyncio

from mindmate.core.config import settings

logger = logging.getLogger(__name__)


class AICore:
    """Core AI interface using Anthropic Claude."""

    def __init__(self):
        """Initialize AI core with Anthropic client."""
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.AI_MODEL
        self.max_tokens = settings.MAX_TOKENS
        self.temperature = settings.TEMPERATURE

    async def generate_response(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate AI response using Claude.

        Args:
            system_prompt: System prompt defining AI behavior
            user_message: Current user message
            conversation_history: Previous conversation messages
            temperature: Override temperature setting
            max_tokens: Override max tokens setting

        Returns:
            AI-generated response text
        """
        try:
            # Build messages list
            messages = []

            # Add conversation history if provided
            if conversation_history:
                for msg in conversation_history:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })

            # Add current user message
            messages.append({
                "role": "user",
                "content": user_message
            })

            # Call Claude API in a thread to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens or self.max_tokens,
                    temperature=temperature or self.temperature,
                    system=system_prompt,
                    messages=messages
                )
            )

            # Extract response text
            if response.content and len(response.content) > 0:
                return response.content[0].text
            else:
                return "I'm having trouble generating a response. Please try again."

        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return "I encountered an error while processing your message. Please try again later."

    async def stream_response(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ):
        """
        Stream AI response using Claude (for future implementation).

        Args:
            system_prompt: System prompt
            user_message: User message
            conversation_history: Conversation history

        Yields:
            Response chunks
        """
        # Placeholder for streaming implementation
        # For now, just return the full response
        response = await self.generate_response(system_prompt, user_message, conversation_history)
        yield response


# Global AI core instance
ai_core = AICore()
ai_core = AICore()
