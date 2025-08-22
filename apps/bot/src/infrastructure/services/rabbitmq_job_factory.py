"""
RabbitMQ job factory implementation for the bot service.
Mirrors the TypeScript implementation for consistency.
"""

import asyncio
import json
import logging
import math
import time
from typing import Any, Dict, Optional

import aio_pika
from aio_pika.abc import AbstractConnection, AbstractChannel, AbstractQueue

from config.settings import settings
from domain.interfaces.job_factory import (
    Job,
    JobFactory,
    JobOptions,
    TaskHandlerArgs,
    TaskHandlerResult,
)
from infrastructure.providers.rabbitmq_provider import RabbitMQProvider


class RabbitMQMessage:
    """RabbitMQ message structure."""
    
    def __init__(self, msg_id: str, data: Any, attempts: int = 0, max_retries: int = 3):
        self.msg_id = msg_id
        self.data = data
        self.attempts = attempts
        self.max_retries = max_retries

    def to_dict(self) -> Dict:
        return {
            "msgId": self.msg_id,
            "data": self.data,
            "attempts": self.attempts,
            "maxRetries": self.max_retries
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "RabbitMQMessage":
        return cls(
            msg_id=data["msgId"],
            data=data["data"],
            attempts=data.get("attempts", 0),
            max_retries=data.get("maxRetries", 3)
        )


class RabbitMQJobFactory(JobFactory):
    """RabbitMQ job factory that uses RabbitMQ for all queue operations."""

    def __init__(self, batch_size: int = 10):
        self.logger = logging.getLogger(__name__)
        self.batch_size = batch_size
        self._channels: Dict[str, AbstractChannel] = {}
        self._workers: Dict[str, bool] = {}
        self._worker_tasks: Dict[str, asyncio.Task] = {}
        
        # RabbitMQ configuration
        self.exchange_name = "telegram_exchange"
        self.dlx_exchange_name = "telegram_dlx_exchange"
        self.max_retries = settings.queue_max_retries
        self.prefetch_count = 10

        self.logger.info("RabbitMQ job factory initialized")

    def create_job(self, options: JobOptions) -> Job:
        """Create a job with the given options."""
        self.logger.info(f"RabbitMQJobFactory - Creating job '{options.name}'")

        return RabbitMQJob(
            job_factory=self,
            options=options,
        )

    async def _get_channel(self, queue_name: str) -> AbstractChannel:
        """Get or create a channel for the given queue."""
        if queue_name in self._channels:
            channel = self._channels[queue_name]
            if not channel.is_closed:
                return channel

        connection = await RabbitMQProvider.get_connection()
        channel = await connection.channel()
        
        # Declare exchanges
        main_exchange = await channel.declare_exchange(
            self.exchange_name, 
            aio_pika.ExchangeType.DIRECT, 
            durable=True
        )
        dlx_exchange = await channel.declare_exchange(
            self.dlx_exchange_name, 
            aio_pika.ExchangeType.DIRECT, 
            durable=True
        )

        # Declare main queue with DLX configuration
        main_queue = await channel.declare_queue(
            queue_name,
            durable=True,
            arguments={
                "x-dead-letter-exchange": self.dlx_exchange_name,
                "x-dead-letter-routing-key": f"{queue_name}.dlq"
            }
        )

        # Declare dead letter queue
        dlq_name = f"{queue_name}.dlq"
        dlq = await channel.declare_queue(dlq_name, durable=True)

        # Bind queues to exchanges
        await main_queue.bind(main_exchange, routing_key=queue_name)
        await dlq.bind(dlx_exchange, routing_key=dlq_name)

        # Set QoS
        await channel.set_qos(prefetch_count=self.prefetch_count)

        self._channels[queue_name] = channel
        self.logger.info(f"Created and configured channel for queue: {queue_name}")

        return channel

    def _generate_message_id(self) -> str:
        """Generate a unique message ID."""
        import random
        import string
        timestamp = str(int(time.time() * 1000))
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
        return f"{timestamp}-{random_suffix}"

    async def close(self) -> None:
        """Clean up all resources."""
        self.logger.info("Shutting down RabbitMQ channels and workers")
        
        # Stop all workers
        for queue_name in list(self._workers.keys()):
            self._workers[queue_name] = False
            
        # Cancel all worker tasks
        for task in self._worker_tasks.values():
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        # Close all channels
        for queue_name, channel in self._channels.items():
            try:
                if not channel.is_closed:
                    await channel.close()
                    self.logger.info(f"Closed channel for queue: {queue_name}")
            except Exception as error:
                self.logger.warning(f"Error closing channel for queue {queue_name}: {error}")
        
        self._channels.clear()
        self._workers.clear()
        self._worker_tasks.clear()


class RabbitMQJob(Job):
    """RabbitMQ job implementation."""

    def __init__(self, job_factory: RabbitMQJobFactory, options: JobOptions):
        self.job_factory = job_factory
        self.options = options
        self.logger = logging.getLogger(__name__)

    async def schedule_task(self, data: Any) -> None:
        """Schedule a task with the given data."""
        try:
            channel = await self.job_factory._get_channel(self.options.name)
            
            message = RabbitMQMessage(
                msg_id=self.job_factory._generate_message_id(),
                data=data,
                attempts=0,
                max_retries=self.job_factory.max_retries
            )

            message_body = aio_pika.Message(
                json.dumps(message.to_dict()).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )

            exchange = await channel.get_exchange(self.job_factory.exchange_name)
            await exchange.publish(
                message_body,
                routing_key=self.options.name
            )

            self.logger.info(f"RabbitMQJobFactory - Scheduled task for job '{self.options.name}'")

        except Exception as e:
            self.logger.error(f"Failed to send message to queue {self.options.name}: {e}")
            raise

    async def turn_on(self) -> None:
        """Start the job worker."""
        if self.job_factory._workers.get(self.options.name, False):
            return

        self.logger.info(f"RabbitMQJobFactory - Turning on worker for job '{self.options.name}'")
        await self._create_worker()

    async def turn_off(self) -> None:
        """Stop the job worker."""
        self.logger.info(f"RabbitMQJobFactory - Turning off worker for job '{self.options.name}'")
        self.job_factory._workers[self.options.name] = False

        # Cancel the worker task
        if self.options.name in self.job_factory._worker_tasks:
            task = self.job_factory._worker_tasks[self.options.name]
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            del self.job_factory._worker_tasks[self.options.name]

    async def _create_worker(self) -> None:
        """Create and start the worker."""
        if not self.options.handler:
            self.logger.info(f"RabbitMQJobFactory - No handler for job '{self.options.name}'")
            return

        self.logger.info(f"RabbitMQJobFactory - Starting worker for job '{self.options.name}'. QueueName: {self.options.name}")
        
        channel = await self.job_factory._get_channel(self.options.name)
        
        # Set this worker as active
        self.job_factory._workers[self.options.name] = True

        # Create worker task
        worker_task = asyncio.create_task(self._worker_loop(channel))
        self.job_factory._worker_tasks[self.options.name] = worker_task

        self.logger.info(f"RabbitMQJobFactory - Worker started for queue: {self.options.name}")

    async def _worker_loop(self, channel: AbstractChannel) -> None:
        """Worker loop that processes messages."""
        try:
            queue = await channel.get_queue(self.options.name)
            
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    if not self.job_factory._workers.get(self.options.name, False):
                        break

                    try:
                        message_content = RabbitMQMessage.from_dict(
                            json.loads(message.body.decode())
                        )
                        
                        self.logger.debug(
                            f"RabbitMQJobFactory - Processing job '{self.options.name}' with id {message_content.msg_id}"
                        )

                        result = await self.options.handler(
                            TaskHandlerArgs(data=message_content.data)
                        )

                        # Handle result based on status
                        if result.status == "error":
                            self.logger.error(
                                f"RabbitMQJobFactory - Job failed '{self.options.name}' with id {message_content.msg_id}: {result.result_message}"
                            )
                            await self._handle_failed_message(channel, message, message_content)
                        elif result.status == "cancelled":
                            self.logger.info(
                                f"RabbitMQJobFactory - Job cancelled '{self.options.name}' with id {message_content.msg_id}"
                            )
                            await message.ack()
                        else:
                            # Success
                            await message.ack()
                            self.logger.info(
                                f"RabbitMQJobFactory - Job completed '{self.options.name}' with id {message_content.msg_id}"
                            )

                    except Exception as error:
                        self.logger.error(f"RabbitMQJobFactory - Error processing job '{self.options.name}': {error}")
                        
                        try:
                            message_content = RabbitMQMessage.from_dict(
                                json.loads(message.body.decode())
                            )
                            await self._handle_failed_message(channel, message, message_content)
                        except Exception:
                            # If we can't parse the message, just nack it
                            message.nack(requeue=False)

        except asyncio.CancelledError:
            self.logger.info(f"Worker for {self.options.name} was cancelled")
            raise
        except Exception as error:
            self.logger.error(f"Error in worker loop for {self.options.name}: {error}")

    async def _handle_failed_message(
        self, 
        channel: AbstractChannel, 
        message: aio_pika.IncomingMessage, 
        message_content: RabbitMQMessage
    ) -> None:
        """Handle a failed message with retry logic."""
        message_content.attempts += 1

        if message_content.attempts >= message_content.max_retries:
            # Send to dead letter queue
            dlq_name = f"{self.options.name}.dlq"
            dlx_exchange = await channel.get_exchange(self.job_factory.dlx_exchange_name)
            
            dlq_message = aio_pika.Message(
                json.dumps(message_content.to_dict()).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )
            
            await dlx_exchange.publish(dlq_message, routing_key=dlq_name)
            
            self.logger.warning(
                f"Message sent to DLQ after {message_content.attempts} attempts: {message_content.msg_id}"
            )
            await message.ack()
        else:
            # Retry: republish the message with updated attempt count
            exchange = await channel.get_exchange(self.job_factory.exchange_name)
            
            # Add delay before retry (exponential backoff)
            delay = min(1000 * (2 ** (message_content.attempts - 1)), 30000) / 1000
            
            # Schedule retry
            asyncio.create_task(self._retry_message(exchange, message_content, delay))
            
            await message.ack()
            self.logger.info(
                f"Message will be retried in {delay}s (attempt {message_content.attempts}/{message_content.max_retries}): {message_content.msg_id}"
            )

    async def _retry_message(
        self, 
        exchange: aio_pika.Exchange, 
        message_content: RabbitMQMessage, 
        delay: float
    ) -> None:
        """Retry a message after a delay."""
        await asyncio.sleep(delay)
        
        retry_message = aio_pika.Message(
            json.dumps(message_content.to_dict()).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        )
        
        await exchange.publish(retry_message, routing_key=self.options.name)
