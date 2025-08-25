"""
Message classifier interface for determining if messages are expense-related.
"""

from abc import ABC, abstractmethod

from domain.entities.message import IncomingMessage


class IMessageClassifier(ABC):
    """Interface for classifying messages as expense-related or not."""

    @abstractmethod
    async def is_expense_related(self, message_text: str) -> bool:
        """
        Determine if a message is related to expenses.
        
        Args:
            message_text: The raw message text from user
            
        Returns:
            True if the message is expense-related, False otherwise
        """
        pass
