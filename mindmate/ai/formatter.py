"""
AI response formatter
"""
import re
from typing import Optional


def format_response(response: str, mode: str = "friend") -> str:
    """
    Format AI response for better readability.

    Args:
        response: Raw AI response
        mode: AI mode (friend, healer, productivity)

    Returns:
        Formatted response
    """
    # Remove excessive newlines
    response = re.sub(r'\n{3,}', '\n\n', response)

    # Trim whitespace
    response = response.strip()

    # Add mode-specific formatting
    if mode == "healer":
        # Add calming emoji for healer mode
        if not response.startswith("🌟"):
            response = f"🌟 {response}"

    elif mode == "productivity":
        # Add productivity emoji
        if not response.startswith("🎯"):
            response = f"🎯 {response}"

    elif mode == "friend":
        # Add friendly emoji
        if not response.startswith("🤗"):
            response = f"🤗 {response}"

    return response


def format_markdown(text: str) -> str:
    """
    Convert markdown to Telegram-compatible format.

    Args:
        text: Text with markdown

    Returns:
        Telegram-formatted text
    """
    # Convert bold: **text** to *text*
    text = re.sub(r'\*\*(.+?)\*\*', r'*\1*', text)

    # Convert italic: _text_ stays the same
    # Convert code: `text` stays the same

    return text


def truncate_response(response: str, max_length: int = 4000) -> str:
    """
    Truncate response if it exceeds Telegram's message limit.

    Args:
        response: Response text
        max_length: Maximum length (Telegram limit is 4096)

    Returns:
        Truncated response
    """
    if len(response) <= max_length:
        return response

    # Truncate and add ellipsis
    return response[:max_length - 20] + "\n\n... (truncated)"


def clean_response(response: str) -> str:
    """
    Clean up AI response by removing unwanted patterns.

    Args:
        response: Raw response

    Returns:
        Cleaned response
    """
    # Remove any system messages or meta-commentary
    response = re.sub(r'\[.*?\]', '', response)

    # Remove excessive punctuation
    response = re.sub(r'[!?]{3,}', '!', response)

    return response.strip()


def add_context_separator(response: str, context_info: Optional[str] = None) -> str:
    """
    Add a separator between context and response.

    Args:
        response: Response text
        context_info: Optional context information

    Returns:
        Response with separator
    """
    if context_info:
        return f"{context_info}\n\n---\n\n{response}"
    return response


def extract_action_items(response: str) -> list:
    """
    Extract action items from AI response.

    Args:
        response: AI response

    Returns:
        List of action items
    """
    action_items = []

    # Look for numbered lists or bullet points
    patterns = [
        r'^\d+\.\s+(.+)$',  # Numbered lists
        r'^[-*]\s+(.+)$',   # Bullet points
    ]

    lines = response.split('\n')
    for line in lines:
        for pattern in patterns:
            match = re.match(pattern, line.strip())
            if match:
                action_items.append(match.group(1))

    return action_items


def highlight_important(text: str) -> str:
    """
    Highlight important words in the response.

    Args:
        text: Response text

    Returns:
        Text with highlighted important words
    """
    # Important keywords to highlight
    important_words = [
        'important', 'critical', 'urgent', 'warning', 'note',
        'remember', 'key', 'essential', 'vital'
    ]

    for word in important_words:
        # Make case-insensitive
        pattern = re.compile(r'\b' + word + r'\b', re.IGNORECASE)
        text = pattern.sub(lambda m: f"*{m.group()}*", text)

    return text
