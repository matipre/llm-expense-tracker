"""
Message processor service - main use case for processing incoming messages with tools.
"""

import logging

from application.jobs.response_sending_job import ResponseSendingJob
from application.services.user_service import UserService
from domain.entities.message import IncomingMessage
from domain.interfaces.expense_parser import IExpenseParser


class MessageProcessorService:
    """Service for processing incoming messages using LLM tools."""

    def __init__(
        self,
        user_service: UserService,
        expense_parser: IExpenseParser,
        response_sending_job: ResponseSendingJob,
    ):
        self.user_service = user_service
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

        # Get or register user
        user, welcome_message = await self.user_service.get_or_register_user(
            message.telegram_user_id, message.message_text
        )
        
        if not user:
            # User not authorized and registration failed
            return
            
        # If this is a new user registration, send welcome message and return
        if welcome_message:
            await self._send_response(message, welcome_message)
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
