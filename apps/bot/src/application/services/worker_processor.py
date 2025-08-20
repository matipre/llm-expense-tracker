"""
Worker processor service for managing job workers lifecycle.
Mirrors the TypeScript implementation for consistency.
"""

import logging

from domain.interfaces.job_factory import Job


class WorkerProcessorService:
    """Service for managing all job workers."""

    def __init__(self, jobs: list[Job]):
        self.logger = logging.getLogger(__name__)
        self._workers = jobs

    async def start_workers(self) -> None:
        """Start all worker processors."""
        self.logger.info("Starting worker processors")

        try:
            # Start message processing worker
            for worker in self._workers:
                await worker.turn_on()
            self.logger.info("MessageProcessing worker started")

        except Exception as e:
            self.logger.error(f"Error starting workers: {e}", exc_info=True)
            raise

    async def stop_workers(self) -> None:
        """Stop all worker processors."""
        self.logger.info("Stopping worker processors")

        try:
            # Stop all workers
            for worker in self._workers:
                await worker.turn_off()

            self.logger.info("All workers stopped")

        except Exception as e:
            self.logger.error(f"Error stopping workers: {e}", exc_info=True)
            raise
