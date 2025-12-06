"""
Healer mode AI engine
"""
from typing import List, Dict, Any
import logging

from mindmate.ai.core import ai_core

logger = logging.getLogger(__name__)


class HealerEngine:
    """AI engine for healer mode - mental health support and therapeutic guidance."""

    def __init__(self):
        """Initialize healer engine."""
        self.system_prompt = """You are a compassionate mental health companion. Your role is to:

1. Provide a safe, non-judgmental space for users to express themselves
2. Listen deeply and validate their emotional experiences
3. Offer therapeutic insights and coping strategies
4. Help users explore their thoughts and feelings
5. Suggest evidence-based techniques for managing stress, anxiety, and difficult emotions
6. Encourage self-reflection and personal growth
7. Recognize when professional help may be needed

Communication style:
- Use calm, soothing language
- Be patient and present
- Ask open-ended questions to facilitate exploration
- Reflect back what you hear to show understanding
- Provide gentle guidance without being prescriptive
- Keep responses thoughtful and measured (2-4 paragraphs)

Techniques to draw from:
- Cognitive Behavioral Therapy (CBT) principles
- Mindfulness and grounding techniques
- Emotional regulation strategies
- Positive psychology approaches

IMPORTANT: You are a supportive companion, not a replacement for professional mental health care.
If someone expresses thoughts of self-harm or suicide, encourage them to seek immediate professional help."""

    async def process(
        self,
        message: str,
        history: List[Dict[str, str]],
        context: Dict[str, Any]
    ) -> str:
        """
        Process user message in healer mode.

        Args:
            message: User message
            history: Conversation history
            context: Additional context

        Returns:
            AI response
        """
        try:
            # Check for crisis keywords
            crisis_keywords = [
                'suicide', 'kill myself', 'end my life', 'want to die',
                'self-harm', 'hurt myself'
            ]

            message_lower = message.lower()
            if any(keyword in message_lower for keyword in crisis_keywords):
                return self._get_crisis_response()

            response = await ai_core.generate_response(
                system_prompt=self.system_prompt,
                user_message=message,
                conversation_history=history,
                temperature=0.7  # Balanced temperature for thoughtful responses
            )
            return response

        except Exception as e:
            logger.error(f"Error in healer engine: {e}")
            return "I'm here to support you. I'm experiencing a technical issue at the moment, but I want you to know that your feelings matter. Please try again in a moment."

    def _get_crisis_response(self) -> str:
        """
        Get response for crisis situations.

        Returns:
            Crisis support message
        """
        return """I'm deeply concerned about what you're sharing. Your life matters, and you deserve support.

Please reach out to professional help immediately:

🆘 Crisis Hotlines:
- National Suicide Prevention Lifeline: 988 (US)
- Crisis Text Line: Text HOME to 741741
- International: findahelpline.com

These services are:
✓ Available 24/7
✓ Free and confidential
✓ Staffed by trained counselors

You don't have to face this alone. Please reach out to one of these resources or a trusted person in your life right now. Your well-being is the top priority. 💚"""
