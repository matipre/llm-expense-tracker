"""
Message processor service - main use case for processing incoming messages.
"""

import logging
from datetime import datetime
from decimal import Decimal

from application.jobs.response_sending_job import ResponseSendingJob
from domain.entities.expense import Expense
from domain.entities.message import IncomingMessage
from domain.entities.user import User
from domain.interfaces.expense_parser import IExpenseParser
from domain.interfaces.expense_repository import IExpenseRepository
from domain.interfaces.user_repository import IUserRepository


class MessageProcessorService:
    """Service for processing incoming messages."""

    def __init__(
        self,
        user_repository: IUserRepository,
        expense_repository: IExpenseRepository,
        expense_parser: IExpenseParser,
        response_sending_job: ResponseSendingJob,
    ):
        self.user_repository = user_repository
        self.expense_repository = expense_repository
        self.expense_parser = expense_parser
        self.response_sending_job = response_sending_job
        self.logger = logging.getLogger(__name__)

    async def process_message(self, message: IncomingMessage) -> None:
        """
        Process an incoming message from the queue.

        Args:
            message: The incoming message to process
        """
        self.logger.info(
            f"Processing message from user {message.telegram_user_id}: {message.message_text}"
        )

        # # Check if user exists in whitelist
        user = await self.user_repository.find_by_telegram_id(str(message.telegram_user_id))
        if not user:
            self.logger.warning(f"User {message.telegram_user_id} not in whitelist, ignoring message")
            return

        # Check if message is about an expense
        is_expense = await self.expense_parser.is_expense_message(message.message_text)
        if not is_expense:
            self.logger.info(
                f"Message from user {message.telegram_user_id} is not about an expense, ignoring"
            )
            return

        # Parse the expense information
        parsed_expense = await self.expense_parser.parse_expense(message.message_text)
        if not parsed_expense:
            self.logger.warning(
                f"Failed to parse expense from message: {message.message_text}"
            )
            await self._send_error_response(
                message, "I couldn't understand your expense. Please try again."
            )
            return

        # Create and save the expense
        expense = Expense(
            id=None,
            user_id=user.id,
            description=parsed_expense.description,
            amount=parsed_expense.amount,
            category=parsed_expense.category,
            added_at=datetime.utcnow(),
        )

        saved_expense = await self.expense_repository.create(expense)
        self.logger.info(f"Saved expense {saved_expense.id} for user {user.id}")

        # Send success response
        response_text = f"{saved_expense.category} expense added ✅"
        await self._send_success_response(message, response_text)

    async def _send_success_response(self, message: IncomingMessage, text: str) -> None:
        """Send a success response back to Telegram."""
        await self.response_sending_job.schedule_response_sending(
            chat_id=message.chat_id, text=text, reply_to_message_id=message.message_id
        )

    async def _send_error_response(self, message: IncomingMessage, text: str) -> None:
        """Send an error response back to Telegram."""
        await self.response_sending_job.schedule_response_sending(
            chat_id=message.chat_id, text=text, reply_to_message_id=message.message_id
        )
