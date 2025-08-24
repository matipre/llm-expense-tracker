"""
Concrete implementation of tool factory for creating expense tools.
"""

from typing import List

from domain.interfaces.expense_categories_repository import IExpenseCategoriesRepository
from domain.interfaces.expense_repository import IExpenseRepository
from domain.interfaces.expense_tool import IExpenseTool
from domain.interfaces.tool_factory import IToolFactory
from infrastructure.tools.add_expense_tool import AddExpenseTool
from infrastructure.tools.get_expenses_by_category_tool import GetExpensesByCategoryTool
from infrastructure.tools.get_recent_expenses_tool import GetRecentExpensesTool


class ExpenseToolFactory(IToolFactory):
    """Factory for creating expense tools with proper user context."""

    def __init__(
        self,
        expense_repository: IExpenseRepository,
        categories_repository: IExpenseCategoriesRepository,
    ):
        """Initialize the tool factory with required repositories.
        
        Args:
            expense_repository: Repository for expense data operations
            categories_repository: Repository for expense categories
        """
        self.expense_repository = expense_repository
        self.categories_repository = categories_repository

    def create_tools_for_user(self, user_id: int) -> List[IExpenseTool]:
        """Create contextualized tools for a specific user.
        
        Args:
            user_id: The ID of the user for whom to create the tools
            
        Returns:
            List of expense tools configured for the specified user
        """
        return [
            AddExpenseTool(
                expense_repository=self.expense_repository,
                categories_repository=self.categories_repository,
                user_id=user_id
            ),
            GetRecentExpensesTool(
                expense_repository=self.expense_repository,
                user_id=user_id
            ),
            GetExpensesByCategoryTool(
                expense_repository=self.expense_repository,
                categories_repository=self.categories_repository,
                user_id=user_id
            ),
        ]
