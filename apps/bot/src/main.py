"""
Main entry point for the Bot Service.
"""

import logging
import os
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from application.jobs.message_processing_job import MessageProcessingJob
from application.jobs.response_sending_job import ResponseSendingJob
from application.services.message_processor import MessageProcessorService
from application.services.worker_processor import WorkerProcessorService
from config.settings import settings
from infrastructure.providers.rabbitmq_provider import RabbitMQProvider
from infrastructure.repositories.expense_repository import PostgreSQLExpenseRepository
from infrastructure.repositories.fixed_expense_categories_repository import FixedExpenseCategoriesRepository
from infrastructure.repositories.user_repository import PostgreSQLUserRepository
from infrastructure.services.expense_tool_factory import ExpenseToolFactory
from infrastructure.services.openai_expense_parser import OpenAIExpenseParser
from infrastructure.services.rabbitmq_job_factory import RabbitMQJobFactory
from presentation.routers.health import router as health_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Global instances
message_processor_service = None
job_factory = None
worker_processor_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global message_processor_service, job_factory, worker_processor_service

    try:
        # Validate settings (skip Supabase validation for now)
        # settings.validate_required_settings()

        # Initialize repositories
        user_repository = PostgreSQLUserRepository(settings.database_url)
        expense_repository = PostgreSQLExpenseRepository(settings.database_url)
        categories_repository = FixedExpenseCategoriesRepository()

        # Initialize tool factory (tools will be created per user per message)
        tool_factory = ExpenseToolFactory(
            expense_repository=expense_repository,
            categories_repository=categories_repository
        )

        # Initialize OpenAI expense parser with tool factory
        openai_expense_parser = OpenAIExpenseParser(
            openai_api_key=settings.openai_api_key,
            tool_factory=tool_factory,
            model=settings.openai_model
        )

        # Initialize RabbitMQ job factory
        job_factory = RabbitMQJobFactory(batch_size=settings.job_batch_size)

        # Initialize jobs first
        response_sending_job = ResponseSendingJob(job_factory)

        # Initialize message processor service with response sending job
        message_processor_service = MessageProcessorService(
            user_repository=user_repository,
            expense_parser=openai_expense_parser,
            response_sending_job=response_sending_job,
        )

        # Initialize message processing job
        message_processing_job = MessageProcessingJob(
            job_factory, message_processor_service
        )

        # Initialize worker processor service
        worker_processor_service = WorkerProcessorService(
            jobs=[message_processing_job.job]
        )

        # Start all workers
        await worker_processor_service.start_workers()

        logger.info("Bot service started successfully")

        yield

        # Cleanup
        await worker_processor_service.stop_workers()
        await job_factory.close()
        await RabbitMQProvider.close_connection()
        await user_repository.close()
        await expense_repository.close()

        logger.info("Bot service stopped")

    except Exception as e:
        logger.error(f"Error during startup: {e}", exc_info=True)
        raise


app = FastAPI(
    title="Darwin Challenge - Bot Service",
    description="Python Bot Service for Telegram Expense Tracking",
    version="1.0.0",
    lifespan=lifespan,
)

# Register routers
app.include_router(health_router, prefix="/health", tags=["health"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower(),
    )
