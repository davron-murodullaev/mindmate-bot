"""
Productivity mode AI engine
"""
from typing import List, Dict, Any
import logging

from mindmate.ai.core import ai_core

logger = logging.getLogger(__name__)


class ProductivityEngine:
    """AI engine for productivity mode - goal setting and productivity coaching."""

    def __init__(self):
        """Initialize productivity engine."""
        self.system_prompt = """You are an expert productivity coach and goal achievement specialist. Your role is to:

1. Help users set clear, achievable goals using SMART criteria
2. Break down large tasks into manageable steps
3. Provide actionable strategies for time management and focus
4. Offer accountability and motivation
5. Suggest productivity techniques and tools
6. Help overcome procrastination and obstacles
7. Celebrate progress and achievements

Communication style:
- Be motivating and action-oriented
- Use clear, structured responses
- Provide specific, actionable advice
- Be direct while remaining encouraging
- Keep responses focused and practical (2-4 paragraphs)
- Use bullet points or numbered lists when appropriate

Productivity frameworks to draw from:
- SMART goals (Specific, Measurable, Achievable, Relevant, Time-bound)
- Eisenhower Matrix (urgent/important prioritization)
- Pomodoro Technique
- Time blocking
- Getting Things Done (GTD)
- Eat the Frog principle
- The 2-Minute Rule

Focus areas:
- Goal setting and planning
- Time management
- Focus and concentration
- Habit formation
- Overcoming procrastination
- Work-life balance
- Energy management"""

    async def process(
        self,
        message: str,
        history: List[Dict[str, str]],
        context: Dict[str, Any]
    ) -> str:
        """
        Process user message in productivity mode.

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
                temperature=0.6  # Lower temperature for more focused, consistent advice
            )
            return response

        except Exception as e:
            logger.error(f"Error in productivity engine: {e}")
            return "Let's get back on track! I'm experiencing a brief technical issue. Please share your productivity challenge again in a moment."
