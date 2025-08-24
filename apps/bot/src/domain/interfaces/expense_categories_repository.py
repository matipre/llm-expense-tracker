"""
Expense categories repository interface.
"""

from abc import ABC, abstractmethod


class IExpenseCategoriesRepository(ABC):
    """Interface for expense categories repository."""

    @abstractmethod
    async def get_all_categories(self) -> list[str]:
        """Get all available expense categories."""
        pass

    @abstractmethod
    async def is_valid_category(self, category: str) -> bool:
        """Check if a category is valid."""
        pass
