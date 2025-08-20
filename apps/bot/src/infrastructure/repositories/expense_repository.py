"""
PostgreSQL expense repository implementation.
"""
import logging
from decimal import Decimal
from typing import List, Optional

import asyncpg

from domain.entities.expense import Expense
from domain.interfaces.expense_repository import IExpenseRepository


class PostgreSQLExpenseRepository(IExpenseRepository):
    """PostgreSQL implementation of expense repository."""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.logger = logging.getLogger(__name__)
        self._pool = None
    
    async def _get_pool(self) -> asyncpg.Pool:
        """Get or create database connection pool."""
        if self._pool is None:
            self._pool = await asyncpg.create_pool(self.database_url)
        return self._pool
    
    async def create(self, expense: Expense) -> Expense:
        """Create a new expense."""
        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    INSERT INTO expenses (user_id, description, amount, category, added_at) 
                    VALUES ($1, $2, $3, $4, $5) 
                    RETURNING id, user_id, description, amount, category, added_at
                    """,
                    expense.user_id,
                    expense.description,
                    float(expense.amount),  # PostgreSQL decimal type expects numeric
                    expense.category,
                    expense.added_at
                )
                
                return Expense(
                    id=row["id"],
                    user_id=row["user_id"],
                    description=row["description"],
                    amount=Decimal(str(row["amount"])),  # Decimal type from PostgreSQL
                    category=row["category"],
                    added_at=row["added_at"]
                )
                
        except Exception as e:
            self.logger.error(f"Error creating expense: {e}", exc_info=True)
            raise
    
    async def find_by_id(self, expense_id: int) -> Optional[Expense]:
        """Find expense by ID."""
        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT id, user_id, description, amount, category, added_at FROM expenses WHERE id = $1",
                    expense_id
                )
                
                if row:
                    return Expense(
                        id=row["id"],
                        user_id=row["user_id"],
                        description=row["description"],
                        amount=Decimal(str(row["amount"])),
                        category=row["category"],
                        added_at=row["added_at"]
                    )
                return None
                
        except Exception as e:
            self.logger.error(f"Error finding expense by id {expense_id}: {e}", exc_info=True)
            raise
    
    async def find_by_user_id(self, user_id: int, limit: int = 100) -> List[Expense]:
        """Find expenses by user ID."""
        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT id, user_id, description, amount, category, added_at 
                    FROM expenses 
                    WHERE user_id = $1 
                    ORDER BY added_at DESC 
                    LIMIT $2
                    """,
                    user_id,
                    limit
                )
                
                expenses = []
                for row in rows:
                    expenses.append(Expense(
                        id=row["id"],
                        user_id=row["user_id"],
                        description=row["description"],
                        amount=Decimal(str(row["amount"])),
                        category=row["category"],
                        added_at=row["added_at"]
                    ))
                
                return expenses
                
        except Exception as e:
            self.logger.error(f"Error finding expenses for user {user_id}: {e}", exc_info=True)
            raise
    
    async def update(self, expense: Expense) -> Expense:
        """Update an existing expense."""
        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    UPDATE expenses 
                    SET description = $2, amount = $3, category = $4, added_at = $5
                    WHERE id = $1 
                    RETURNING id, user_id, description, amount, category, added_at
                    """,
                    expense.id,
                    expense.description,
                    float(expense.amount),
                    expense.category,
                    expense.added_at
                )
                
                if not row:
                    raise ValueError(f"Expense with id {expense.id} not found")
                
                return Expense(
                    id=row["id"],
                    user_id=row["user_id"],
                    description=row["description"],
                    amount=Decimal(str(row["amount"])),
                    category=row["category"],
                    added_at=row["added_at"]
                )
                
        except Exception as e:
            self.logger.error(f"Error updating expense {expense.id}: {e}", exc_info=True)
            raise
    
    async def delete(self, expense_id: int) -> bool:
        """Delete an expense by ID."""
        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                result = await conn.execute(
                    "DELETE FROM expenses WHERE id = $1",
                    expense_id
                )
                
                return result == "DELETE 1"
                
        except Exception as e:
            self.logger.error(f"Error deleting expense {expense_id}: {e}", exc_info=True)
            raise
    
    async def close(self) -> None:
        """Close database connections."""
        if self._pool:
            await self._pool.close()
            self._pool = None
