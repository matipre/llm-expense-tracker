"""
User repository interface.
"""
from abc import ABC, abstractmethod
from typing import Optional

from domain.entities.user import User


class IUserRepository(ABC):
    """Interface for user repository."""
    
    @abstractmethod
    async def find_by_telegram_id(self, telegram_id: str) -> Optional[User]:
        """Find user by Telegram ID."""
        pass
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user."""
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """Update an existing user."""
        pass
    
    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        """Delete a user by ID."""
        pass
