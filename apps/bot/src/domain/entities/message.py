"""
Message domain entities.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class IncomingMessage:
    """Represents a message received from the queue."""

    telegram_user_id: int
    chat_id: int
    message_text: str
    timestamp: datetime
    message_id: int

    def __post_init__(self):
        """Validate message data after initialization."""
        if not self.message_text:
            raise ValueError("Message text is required")

        if not self.telegram_user_id:
            raise ValueError("Telegram user ID is required")

        if not self.chat_id:
            raise ValueError("Chat ID is required")


@dataclass
class ParsedExpense:
    """Represents a parsed expense from a message."""

    description: str
    amount: Decimal
    category: str
    confidence_score: float

    def __post_init__(self):
        """Validate parsed expense data."""
        if not self.description:
            raise ValueError("Description is required")

        if self.amount is None:
            raise ValueError("Amount is required")

        if not isinstance(self.amount, Decimal):
            self.amount = Decimal(str(self.amount))

        if not self.category:
            raise ValueError("Category is required")

        if not (0.0 <= self.confidence_score <= 1.0):
            raise ValueError("Confidence score must be between 0.0 and 1.0")


@dataclass
class BotResponse:
    """Represents a response to be sent back to Telegram."""

    chat_id: int
    text: str
    reply_to_message_id: int | None = None
