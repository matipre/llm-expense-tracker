"""
Expense parser interface for LLM integration.
"""

from abc import ABC, abstractmethod

from domain.entities.message import ParsedExpense


class IExpenseParser(ABC):
    """Interface for parsing expenses from text using LLM."""

    @abstractmethod
    async def parse_expense(self, message_text: str) -> ParsedExpense | None:
        """
        Parse expense information from message text.

        Args:
            message_text: The raw message text from user

        Returns:
            ParsedExpense if the message contains expense information, None otherwise
        """
        pass

    @abstractmethod
    async def is_expense_message(self, message_text: str) -> bool:
        """
        Determine if a message contains expense information.

        Args:
            message_text: The raw message text from user

        Returns:
            True if the message appears to be about an expense, False otherwise
        """
        pass
