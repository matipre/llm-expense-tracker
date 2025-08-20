"""
Worker processor service for managing job workers lifecycle.
Mirrors the TypeScript implementation for consistency.
"""
import logging
from typing import List

from application.jobs.message_processing_job import MessageProcessingJob
from application.jobs.response_sending_job import ResponseSendingJob


class WorkerProcessorService:
    """Service for managing all job workers."""
    
    def __init__(self, message_processing_job: MessageProcessingJob, response_sending_job: ResponseSendingJob):
        self.message_processing_job = message_processing_job
        self.response_sending_job = response_sending_job
        self.logger = logging.getLogger(__name__)
        self._workers: List[MessageProcessingJob | ResponseSendingJob] = [
            message_processing_job,
            response_sending_job
        ]
    
    async def start_workers(self) -> None:
        """Start all worker processors."""
        self.logger.info("Starting worker processors")
        
        try:
            # Start message processing worker
            await self.message_processing_job.job.turn_on()
            self.logger.info("MessageProcessing worker started")
            
            # Start response sending worker
            await self.response_sending_job.job.turn_on()
            self.logger.info("ResponseSending worker started")
            
        except Exception as e:
            self.logger.error(f"Error starting workers: {e}", exc_info=True)
            raise
    
    async def stop_workers(self) -> None:
        """Stop all worker processors."""
        self.logger.info("Stopping worker processors")
        
        try:
            # Stop all workers
            for worker in self._workers:
                await worker.job.turn_off()
            
            self.logger.info("All workers stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping workers: {e}", exc_info=True)
            raise
