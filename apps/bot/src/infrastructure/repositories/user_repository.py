"""
PostgreSQL user repository implementation.
"""

import logging

import asyncpg

from domain.entities.user import User
from domain.interfaces.user_repository import IUserRepository


class PostgreSQLUserRepository(IUserRepository):
    """PostgreSQL implementation of user repository."""

    def __init__(self, database_url: str):
        self.database_url = database_url
        self.logger = logging.getLogger(__name__)
        self._pool = None

    async def _get_pool(self) -> asyncpg.Pool:
        """Get or create database connection pool."""
        if self._pool is None:
            self._pool = await asyncpg.create_pool(self.database_url)
        return self._pool

    async def find_by_telegram_id(self, telegram_id: str) -> User | None:
        """Find user by Telegram ID."""
        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT id, telegram_id FROM users WHERE telegram_id = $1",
                    telegram_id,
                )

                if row:
                    return User(id=row["id"], telegram_id=row["telegram_id"])
                return None

        except Exception as e:
            self.logger.error(
                f"Error finding user by telegram_id {telegram_id}: {e}", exc_info=True
            )
            raise

    async def create(self, user: User) -> User:
        """Create a new user."""
        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                row = await conn.fetchrow(
                    "INSERT INTO users (telegram_id) VALUES ($1) RETURNING id, telegram_id",
                    user.telegram_id,
                )

                return User(id=row["id"], telegram_id=row["telegram_id"])

        except Exception as e:
            self.logger.error(
                f"Error creating user {user.telegram_id}: {e}", exc_info=True
            )
            raise

    async def update(self, user: User) -> User:
        """Update an existing user."""
        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                row = await conn.fetchrow(
                    "UPDATE users SET telegram_id = $2 WHERE id = $1 RETURNING id, telegram_id",
                    user.id,
                    user.telegram_id,
                )

                if not row:
                    raise ValueError(f"User with id {user.id} not found")

                return User(id=row["id"], telegram_id=row["telegram_id"])

        except Exception as e:
            self.logger.error(f"Error updating user {user.id}: {e}", exc_info=True)
            raise

    async def delete(self, user_id: int) -> bool:
        """Delete a user by ID."""
        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                result = await conn.execute("DELETE FROM users WHERE id = $1", user_id)

                return result == "DELETE 1"

        except Exception as e:
            self.logger.error(f"Error deleting user {user_id}: {e}", exc_info=True)
            raise

    async def close(self) -> None:
        """Close database connections."""
        if self._pool:
            await self._pool.close()
            self._pool = None
