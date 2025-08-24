"""
Expense domain entity.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

# Note: Expense categories are now managed via IExpenseCategoriesRepository
# This maintains backward compatibility for any existing imports


@dataclass
class Expense:
    """Expense domain entity."""

    id: int | None
    user_id: int
    description: str
    amount: Decimal
    category: str
    added_at: datetime

    def __post_init__(self):
        """Validate expense data after initialization."""
        if not self.description:
            raise ValueError("Description is required")

        if self.amount is None:
            raise ValueError("Amount is required")

        if not isinstance(self.amount, Decimal):
            self.amount = Decimal(str(self.amount))

        if not self.category:
            raise ValueError("Category is required")

        # Note: Category validation is now handled by the service layer
        # using IExpenseCategoriesRepository

        if not self.added_at:
            self.added_at = datetime.utcnow()

    @staticmethod
    def get_valid_categories() -> list[str]:
        """
        Get list of valid expense categories.
        
        Note: This method is deprecated. Use IExpenseCategoriesRepository instead.
        """
        # Backward compatibility - import here to avoid circular dependencies
        from infrastructure.repositories.fixed_expense_categories_repository import FIXED_EXPENSE_CATEGORIES
        return FIXED_EXPENSE_CATEGORIES.copy()
