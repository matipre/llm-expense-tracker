"""
Tool factory interface for creating contextualized expense tools.
"""

from abc import ABC, abstractmethod
from typing import List

from domain.interfaces.expense_tool import IExpenseTool


class IToolFactory(ABC):
    """Interface for creating expense tools with user context."""

    @abstractmethod
    def create_tools_for_user(self, user_id: int) -> List[IExpenseTool]:
        """Create a list of expense tools contextualized for a specific user.
        
        Args:
            user_id: The ID of the user for whom to create the tools
            
        Returns:
            List of expense tools ready to use for the specified user
        """
        pass
