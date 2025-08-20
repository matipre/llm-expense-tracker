"""
Main entry point for the Bot Service.
"""
import asyncio
import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import settings
from presentation.routers.health import router as health_router
from infrastructure.services.openai_expense_parser import OpenAIExpenseParser
from infrastructure.services.supabase_job_factory import SupabaseJobFactory
from infrastructure.providers.supabase_provider import SupabaseProvider
from infrastructure.repositories.user_repository import PostgreSQLUserRepository
from infrastructure.repositories.expense_repository import PostgreSQLExpenseRepository
from application.services.message_processor import MessageProcessorService
from application.services.worker_processor import WorkerProcessorService
from application.jobs.message_processing_job import MessageProcessingJob
from application.jobs.response_sending_job import ResponseSendingJob

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Global instances
message_processor_service = None
queue_service = None
worker_processor_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global message_processor_service, queue_service, worker_processor_service
    
    try:
        # Validate settings
        settings.validate_required_settings()
        
        # Initialize dependencies
        expense_parser = OpenAIExpenseParser(
            openai_api_key=settings.openai_api_key,
            model=settings.openai_model
        )
        
        user_repository = PostgreSQLUserRepository(settings.database_url)
        expense_repository = PostgreSQLExpenseRepository(settings.database_url)
        
        # Initialize Supabase client and services
        supabase_client = SupabaseProvider.get_client()
        
        # Initialize job factory with configurable settings
        job_factory = SupabaseJobFactory(
            supabase_client=supabase_client,
            batch_size=settings.job_batch_size
        )
        
        # Initialize jobs first
        response_sending_job = ResponseSendingJob(job_factory)
        
        # Initialize message processor service with response sending job
        message_processor_service = MessageProcessorService(
            user_repository=user_repository,
            expense_repository=expense_repository,
            expense_parser=expense_parser,
            response_sending_job=response_sending_job
        )
        
        # Initialize message processing job
        message_processing_job = MessageProcessingJob(job_factory, message_processor_service)
        
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
    lifespan=lifespan
)

# Register routers
app.include_router(health_router, prefix="/health", tags=["health"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0", 
        port=settings.port,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower()
    )
