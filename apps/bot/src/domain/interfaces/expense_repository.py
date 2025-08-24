"""
Expense repository interface.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal

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
    async def find_by_user_id_and_date_range(
        self, 
        user_id: int, 
        start_date: datetime, 
        end_date: datetime,
        limit: int = 100
    ) -> list[Expense]:
        """Find expenses by user ID within a date range."""
        pass

    @abstractmethod
    async def get_summary_by_category(
        self, 
        user_id: int, 
        start_date: datetime, 
        end_date: datetime
    ) -> dict[str, Decimal]:
        """Get expense summary grouped by category within date range."""
        pass

    @abstractmethod
    async def update(self, expense: Expense) -> Expense:
        """Update an existing expense."""
        pass

    @abstractmethod
    async def delete(self, expense_id: int) -> bool:
        """Delete an expense by ID."""
        pass
