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
from infrastructure.services.supabase_queue_service import SupabaseQueueService
from infrastructure.providers.supabase_provider import SupabaseProvider
from infrastructure.repositories.user_repository import PostgreSQLUserRepository
from infrastructure.repositories.expense_repository import PostgreSQLExpenseRepository
from application.services.message_processor import MessageProcessorService

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Global instances
message_processor_service = None
queue_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global message_processor_service, queue_service
    
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
        
        # Use unified Supabase queue service with injected client
        supabase_client = SupabaseProvider.get_client()
        queue_service = SupabaseQueueService(supabase_client)
        
        message_processor_service = MessageProcessorService(
            user_repository=user_repository,
            expense_repository=expense_repository,
            expense_parser=expense_parser,
            queue_service=queue_service
        )
        
        # Start queue consumer
        await queue_service.start_consumer()
        
        # Set up the consumer loop with proper injection
        async def consume_messages():
            while True:
                try:
                    await queue_service.consume_messages(message_processor_service.process_message)
                    await asyncio.sleep(settings.queue_poll_interval)
                except Exception as e:
                    logger.error(f"Error in consumer loop: {e}", exc_info=True)
                    await asyncio.sleep(10)
        
        # Start the consumer task
        consumer_task = asyncio.create_task(consume_messages())
        
        logger.info("Bot service started successfully")
        
        yield
        
        # Cleanup
        consumer_task.cancel()
        await queue_service.stop_consumer()
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
