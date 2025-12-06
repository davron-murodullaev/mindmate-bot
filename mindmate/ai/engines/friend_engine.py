"""
Friend mode AI engine
"""
from typing import List, Dict, Any
import logging

from mindmate.ai.core import ai_core

logger = logging.getLogger(__name__)


class FriendEngine:
    """AI engine for friend mode - supportive and empathetic conversations."""

    def __init__(self):
        """Initialize friend engine."""
        self.system_prompt = """You are a supportive, empathetic friend. Your role is to:

1. Listen actively and validate the user's feelings
2. Provide emotional support and encouragement
3. Be conversational, warm, and authentic
4. Ask thoughtful follow-up questions
5. Share relatable experiences when appropriate
6. Help users feel heard and understood
7. Maintain a positive, uplifting tone

Communication style:
- Use casual, friendly language
- Show genuine interest in what they share
- Be empathetic without being overly formal
- Use humor appropriately to lighten the mood
- Keep responses concise and natural (2-4 paragraphs)

Remember: You're a friend, not a therapist. Focus on emotional support and companionship."""

    async def process(
        self,
        message: str,
        history: List[Dict[str, str]],
        context: Dict[str, Any]
    ) -> str:
        """
        Process user message in friend mode.

        Args:
            message: User message
            history: Conversation history
            context: Additional context

        Returns:
            AI response
        """
        try:
            response = await ai_core.generate_response(
                system_prompt=self.system_prompt,
                user_message=message,
                conversation_history=history,
                temperature=0.8  # Higher temperature for more natural conversation
            )
            return response

        except Exception as e:
            logger.error(f"Error in friend engine: {e}")
            return "I'm here for you! Though I'm having a small technical hiccup right now. Can you try telling me again?"
