"""
Message processor service - main use case for processing incoming messages with tools.
"""

import logging

from application.jobs.response_sending_job import ResponseSendingJob
from domain.entities.message import IncomingMessage
from domain.interfaces.expense_parser import IExpenseParser
from domain.interfaces.user_repository import IUserRepository


class MessageProcessorService:
    """Service for processing incoming messages using LLM tools."""

    def __init__(
        self,
        user_repository: IUserRepository,
        expense_parser: IExpenseParser,
        response_sending_job: ResponseSendingJob,
    ):
        self.user_repository = user_repository
        self.expense_parser = expense_parser
        self.response_sending_job = response_sending_job
        self.logger = logging.getLogger(__name__)

    async def process_message(self, message: IncomingMessage) -> None:
        """
        Process an incoming message using LLM with tools.

        Args:
            message: The incoming message to process
        """
        self.logger.info(
            "Processing message from user %s: %s",
            message.telegram_user_id,
            message.message_text
        )

        # Check if user exists in whitelist
        user = await self.user_repository.find_by_telegram_id(
            str(message.telegram_user_id)
        )
        if not user:
            self.logger.warning(
                "User %s not in whitelist, ignoring message",
                message.telegram_user_id
            )
            return

        # Process message using LLM with tools
        result = await self.expense_parser.process_message(
            message.message_text, user.id
        )
        
        if not result.success:
            self.logger.error("Failed to process message: %s", result.response_text)
        
        # Always send the response from the LLM
        await self._send_response(message, result.response_text)

    async def _send_response(self, message: IncomingMessage, text: str) -> None:
        """Send a response back to Telegram."""
        await self.response_sending_job.schedule_response_sending(
            chat_id=message.chat_id, text=text, reply_to_message_id=message.message_id
        )
