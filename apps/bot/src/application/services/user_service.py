"""
User service - handles user retrieval, registration and management.
"""

import logging

from domain.entities.user import User
from domain.interfaces.user_repository import IUserRepository


class UserService:
    """Service for managing users including registration and retrieval."""

    def __init__(
        self,
        user_repository: IUserRepository,
        registration_password: str,
    ):
        self.user_repository = user_repository
        self.registration_password = registration_password
        self.logger = logging.getLogger(__name__)

    async def get_or_register_user(self, telegram_user_id: int, message_text: str) -> tuple[User | None, str | None]:
        """
        Get existing user or register new user if password matches.
        
        Args:
            telegram_user_id: Telegram user ID
            message_text: The message text to check against registration password
            
        Returns:
            Tuple of (User or None, welcome_message or None)
            - If user exists: (User, None)
            - If user doesn't exist and password matches: (User, welcome_message)
            - If user doesn't exist and password doesn't match: (None, None)
        """
        # Check if user exists
        user = await self.user_repository.find_by_telegram_id(
            str(telegram_user_id)
        )
        
        if user:
            self.logger.debug("Found existing user with telegram_id: %s", telegram_user_id)
            return user, None
            
        # User doesn't exist - check if message matches registration password
        if message_text.strip() == self.registration_password:
            self.logger.info(
                "Registering new user with telegram_id: %s",
                telegram_user_id
            )
            
            # Create new user
            new_user = User(id=None, telegram_id=str(telegram_user_id))
            user = await self.user_repository.create(new_user)
            
            # Return user and welcome message
            welcome_message = self._get_welcome_message()
            return user, welcome_message
        else:
            self.logger.warning(
                "User %s not in whitelist and incorrect registration password, ignoring message",
                telegram_user_id
            )
            return None, None

    def _get_welcome_message(self) -> str:
        """Get welcome message for new users."""
        return """Welcome to your personal Expense Tracking Bot! 🎉

I'm here to help you track and manage your expenses with ease. Here's what I can do for you:

📝 Adding Expenses:
Just tell me about your expenses in natural language! For example:
- "I spent $25 on lunch at McDonald's"
- "Coffee $4.50"

📊 Viewing Your Expenses:
- "Show me my recent expenses"
- "What did I spend on food this month?"

💡 Smart Features:
- I automatically categorize your expenses (Food, Transportation, Shopping, etc.)
- I understand various formats and currencies

Start by telling me about your first expense, and I'll take care of the rest! 💰"""
