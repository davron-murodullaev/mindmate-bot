"""
User service
"""
from typing import Optional, Dict, Any
import logging

from mindmate.db.queries import create_user, get_user, update_user_language, update_user_timezone

logger = logging.getLogger(__name__)


class UserService:
    """Service for user management."""

    @staticmethod
    async def get_or_create_user(
        user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        language_code: str = "en"
    ) -> Dict[str, Any]:
        """
        Get existing user or create new one.

        Args:
            user_id: Telegram user ID
            username: Username
            first_name: First name
            last_name: Last name
            language_code: Language code

        Returns:
            User dictionary
        """
        try:
            # Try to get existing user
            user = await get_user(user_id)

            if not user:
                # Create new user
                await create_user(user_id, username, first_name, last_name, language_code)
                user = await get_user(user_id)
                logger.info(f"Created new user {user_id}")
            else:
                # Update user info
                await create_user(user_id, username, first_name, last_name, user['language_code'])
                logger.info(f"Updated user {user_id}")

            return user or {}

        except Exception as e:
            logger.error(f"Error in get_or_create_user: {e}")
            return {
                'user_id': user_id,
                'language_code': language_code,
                'username': username,
                'first_name': first_name,
                'last_name': last_name
            }

    @staticmethod
    async def get_user_language(user_id: int) -> str:
        """
        Get user's language preference.

        Args:
            user_id: User ID

        Returns:
            Language code (default: 'en')
        """
        try:
            user = await get_user(user_id)
            return user['language_code'] if user else 'en'

        except Exception as e:
            logger.error(f"Error getting user language: {e}")
            return 'en'

    @staticmethod
    async def set_user_language(user_id: int, language_code: str) -> bool:
        """
        Set user's language preference.

        Args:
            user_id: User ID
            language_code: Language code

        Returns:
            True if successful, False otherwise
        """
        try:
            await update_user_language(user_id, language_code)
            logger.info(f"Updated language for user {user_id} to {language_code}")
            return True

        except Exception as e:
            logger.error(f"Error setting user language: {e}")
            return False

    @staticmethod
    async def set_user_timezone(user_id: int, timezone: str) -> bool:
        """
        Set user's timezone.

        Args:
            user_id: User ID
            timezone: Timezone string

        Returns:
            True if successful, False otherwise
        """
        try:
            await update_user_timezone(user_id, timezone)
            logger.info(f"Updated timezone for user {user_id} to {timezone}")
            return True

        except Exception as e:
            logger.error(f"Error setting user timezone: {e}")
            return False


# Global service instance
user_service = UserService()
