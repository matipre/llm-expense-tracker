"""
Expense repository interface.
"""

from abc import ABC, abstractmethod

from domain.entities.expense import Expense


class IExpenseRepository(ABC):
    """Interface for expense repository."""

    @abstractmethod
    async def create(self, expense: Expense) -> Expense:
        """Create a new expense."""
        pass

    @abstractmethod
    async def find_by_id(self, expense_id: int) -> Expense | None:
        """Find expense by ID."""
        pass

    @abstractmethod
    async def find_by_user_id(self, user_id: int, limit: int = 100) -> list[Expense]:
        """Find expenses by user ID."""
        pass

    @abstractmethod
    async def update(self, expense: Expense) -> Expense:
        """Update an existing expense."""
        pass

    @abstractmethod
    async def delete(self, expense_id: int) -> bool:
        """Delete an expense by ID."""
        pass
