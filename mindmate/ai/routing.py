"""
AI mode routing
"""
from typing import List, Dict, Any
import logging

from mindmate.ai.engines.friend_engine import FriendEngine
from mindmate.ai.engines.healer_engine import HealerEngine
from mindmate.ai.engines.productivity_engine import ProductivityEngine

logger = logging.getLogger(__name__)


async def route_to_engine(
    mode: str,
    message: str,
    history: List[Dict[str, str]],
    context: Dict[str, Any]
) -> str:
    """
    Route message to appropriate AI engine based on mode.

    Args:
        mode: AI mode (friend, healer, productivity)
        message: User message
        history: Conversation history
        context: Additional context

    Returns:
        AI-generated response
    """
    try:
        if mode == "friend":
            engine = FriendEngine()
            return await engine.process(message, history, context)

        elif mode == "healer":
            engine = HealerEngine()
            return await engine.process(message, history, context)

        elif mode == "productivity":
            engine = ProductivityEngine()
            return await engine.process(message, history, context)

        else:
            logger.warning(f"Unknown AI mode: {mode}, defaulting to friend")
            engine = FriendEngine()
            return await engine.process(message, history, context)

    except Exception as e:
        logger.error(f"Error routing to AI engine: {e}")
        return "I'm having trouble processing your message right now. Please try again later."


def get_mode_description(mode: str) -> str:
    """
    Get description for an AI mode.

    Args:
        mode: AI mode name

    Returns:
        Mode description
    """
    descriptions = {
        "friend": "A supportive friend who listens and provides emotional support",
        "healer": "A mental health companion providing therapeutic guidance",
        "productivity": "A productivity expert helping you achieve your goals"
    }
    return descriptions.get(mode, "AI companion")


def get_available_modes() -> List[Dict[str, str]]:
    """
    Get list of available AI modes.

    Returns:
        List of mode dictionaries with name, description, and icon
    """
    return [
        {
            "name": "friend",
            "description": "A supportive friend who listens and provides emotional support",
            "icon": "🤗"
        },
        {
            "name": "healer",
            "description": "A mental health companion providing therapeutic guidance",
            "icon": "🌟"
        },
        {
            "name": "productivity",
            "description": "A productivity expert helping you achieve your goals",
            "icon": "🎯"
        }
    ]
