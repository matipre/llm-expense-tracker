"""
Message processing job for consuming and processing incoming Telegram messages.
"""
import logging
from datetime import datetime
from typing import Any

from application.services.message_processor import MessageProcessorService
from domain.interfaces.job_factory import JobFactory, JobOptions, TaskHandlerArgs
from domain.entities.message import IncomingMessage
from infrastructure.utils.queue_utils import create_success_result, create_error_result


class MessageProcessingJob:
    """Job for processing incoming Telegram messages."""
    
    def __init__(self, job_factory: JobFactory, message_processor_service: MessageProcessorService):
        self.job_factory = job_factory
        self.message_processor_service = message_processor_service
        self.logger = logging.getLogger(__name__)
        
        # Create the job with handler
        self.job = self.job_factory.create_job(JobOptions(
            name='telegram_received_messages',
            handler=self._handle_message
        ))
    
    async def _handle_message(self, args: TaskHandlerArgs) -> Any:
        """Handle incoming message processing."""
        try:
            # Parse the message data
            data = args.data
            message = IncomingMessage(
                telegram_user_id=data['telegramUserId'],
                chat_id=data['chatId'],
                message_text=data['messageText'],
                timestamp=datetime.fromisoformat(data['timestamp'].replace('Z', '')),
                message_id=data['messageId']
            )
            
            # Process the message
            await self.message_processor_service.process_message(message)
            
            return create_success_result(f"Message processed for chat {message.chat_id}")
            
        except Exception as e:
            self.logger.error(f"Error processing message: {e}", exc_info=True)
            return create_error_result(f"Failed to process message: {str(e)}")
    
    async def schedule_message_processing(self, chat_id: int, message_text: str, 
                                        telegram_user_id: int, timestamp: str, message_id: int) -> None:
        """Schedule message processing."""
        await self.job.schedule_task({
            'chatId': chat_id,
            'messageText': message_text,
            'telegramUserId': telegram_user_id,
            'timestamp': timestamp,
            'messageId': message_id
        })
