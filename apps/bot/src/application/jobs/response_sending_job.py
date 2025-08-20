"""
Response sending job for sending bot responses back to the connector service.
"""
import logging
from typing import Any

from domain.interfaces.job_factory import JobFactory, Job, JobOptions


class ResponseSendingJob:
    """Job for sending bot responses."""
    
    def __init__(self, job_factory: JobFactory):
        self.job_factory = job_factory
        self.logger = logging.getLogger(__name__)
        
        # Create the job with handler
        self.job = self.job_factory.create_job(JobOptions(
            name='telegram_bot_responses'
        ))
    
    async def schedule_response_sending(self, chat_id: int, text: str, reply_to_message_id: int = None) -> None:
        """Schedule response sending."""
        await self.job.schedule_task({
            'chatId': chat_id,
            'text': text,
            'replyToMessageId': reply_to_message_id
        })
