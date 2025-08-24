"""
Expense parser interface for LLM integration with tools.
"""

from abc import ABC, abstractmethod

from domain.entities.message import ProcessingResult


class IExpenseParser(ABC):
    """Interface for processing messages using LLM with tools."""

    @abstractmethod
    async def process_message(
        self, 
        message_text: str, 
        user_id: int
    ) -> ProcessingResult:
        """
        Process a message using LLM with tools.
        
        The LLM can decide to:
        - Add a new expense
        - Query recent expenses
        - Query expenses by category
        - Provide a general chat response
        
        Args:
            message_text: The raw message text from user
            user_id: The ID of the user sending the message
            
        Returns:
            ProcessingResult containing the outcome and response text
        """
        pass
