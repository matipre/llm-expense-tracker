"""
User domain entity.
"""

from dataclasses import dataclass


@dataclass
class User:
    """User domain entity."""

    id: int | None
    telegram_id: str

    def __post_init__(self):
        """Validate user data after initialization."""
        if not self.telegram_id:
            raise ValueError("Telegram ID is required")

        if not isinstance(self.telegram_id, str):
            self.telegram_id = str(self.telegram_id)
