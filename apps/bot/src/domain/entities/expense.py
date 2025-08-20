"""
Expense domain entity.
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


# Predefined expense categories
EXPENSE_CATEGORIES = [
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
    "Other"
]


@dataclass
class Expense:
    """Expense domain entity."""
    id: Optional[int]
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
            
        if self.category not in EXPENSE_CATEGORIES:
            raise ValueError(f"Category must be one of: {', '.join(EXPENSE_CATEGORIES)}")
            
        if not self.added_at:
            self.added_at = datetime.utcnow()
    
    @staticmethod
    def get_valid_categories() -> list[str]:
        """Get list of valid expense categories."""
        return EXPENSE_CATEGORIES.copy()
