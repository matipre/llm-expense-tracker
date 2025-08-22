"""
RabbitMQ connection provider for the bot service.
"""

import asyncio
import logging
from typing import Optional

import aio_pika

from config.settings import settings


class RabbitMQProvider:
    """Factory for creating RabbitMQ connection instances."""

    _connection: Optional[aio_pika.abc.AbstractConnection] = None
    _logger = logging.getLogger(__name__)

    @classmethod
    async def get_connection(cls) -> aio_pika.abc.AbstractConnection:
        """Get or create a RabbitMQ connection instance (singleton pattern)."""
        if cls._connection is None or cls._connection.is_closed:
            cls._connection = await cls._create_connection()
        return cls._connection

    @classmethod
    async def _create_connection(cls) -> aio_pika.abc.AbstractConnection:
        """Create a new RabbitMQ connection with retry logic."""
        max_retries = 5
        retry_delay = 5.0
        
        if not settings.rabbitmq_url:
            raise ValueError("RabbitMQ configuration missing: RABBITMQ_URL required")

        for attempt in range(1, max_retries + 1):
            try:
                cls._logger.info(f"Attempting to connect to RabbitMQ (attempt {attempt}/{max_retries})")
                connection = await aio_pika.connect_robust(settings.rabbitmq_url)
                
                cls._logger.info("Successfully connected to RabbitMQ")
                return connection
                
            except Exception as error:
                cls._logger.warning(
                    f"Failed to connect to RabbitMQ (attempt {attempt}/{max_retries}): {error}"
                )
                
                if attempt < max_retries:
                    cls._logger.info(f"Retrying in {retry_delay}s...")
                    await asyncio.sleep(retry_delay)
                else:
                    cls._logger.error("Failed to connect to RabbitMQ after all retries")
                    raise



    @classmethod
    async def close_connection(cls) -> None:
        """Close the RabbitMQ connection."""
        if cls._connection and not cls._connection.is_closed:
            await cls._connection.close()
            cls._logger.info("RabbitMQ connection closed")
