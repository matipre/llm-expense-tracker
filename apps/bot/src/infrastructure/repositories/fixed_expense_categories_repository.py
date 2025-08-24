"""
Fixed expense categories repository implementation.
"""

from domain.interfaces.expense_categories_repository import IExpenseCategoriesRepository

# Fixed expense categories
FIXED_EXPENSE_CATEGORIES = [
    "Housing",
    "Transportation", 
    "Food",
    "Utilities",
    "Insurance",
    "Medical/Healthcare",
    "Savings",
    "Debt",
    "Education",
    "Entertainment",
    "Other",
]


class FixedExpenseCategoriesRepository(IExpenseCategoriesRepository):
    """Fixed implementation of expense categories repository."""

    async def get_all_categories(self) -> list[str]:
        """Get all available expense categories."""
        return FIXED_EXPENSE_CATEGORIES.copy()

    async def is_valid_category(self, category: str) -> bool:
        """Check if a category is valid."""
        return category in FIXED_EXPENSE_CATEGORIES
