"""
Supabase job factory implementation for the bot service.
Mirrors the TypeScript implementation for consistency.
"""
import asyncio
import logging
from typing import Any, Dict

from supabase import Client

from domain.interfaces.job_factory import JobFactory, Job, JobOptions, TaskHandlerArgs, TaskHandlerResult


class SupabaseJobFactory(JobFactory):
    """Supabase job factory that uses Supabase Queues (pgmq) for all queue operations."""
    
    def __init__(self, supabase_client: Client, batch_size: int = 10):
        self.supabase: Client = supabase_client
        self.logger = logging.getLogger(__name__)
        self.batch_size = batch_size
        self._workers: Dict[str, asyncio.Task] = {}
        
        self.logger.info("Supabase job factory initialized")
    
    def create_job(self, options: JobOptions) -> Job:
        """Create a job with the given options."""
        self.logger.info(f"Creating job '{options.name}'")
        
        return SupabaseJob(
            supabase_client=self.supabase,
            options=options,
            batch_size=self.batch_size,
            workers=self._workers
        )


class SupabaseJob(Job):
    """Supabase job implementation."""
    
    def __init__(self, supabase_client: Client, options: JobOptions, batch_size: int, workers: Dict[str, asyncio.Task]):
        self.supabase = supabase_client
        self.options = options
        self.batch_size = batch_size
        self.workers = workers
        self.logger = logging.getLogger(__name__)
        self._running = False
    
    async def schedule_task(self, data: Any) -> None:
        """Schedule a task with the given data."""
        try:
            response = self.supabase.schema('pgmq_public').rpc('send', {
                'queue_name': self.options.name,
                'message': {'data': data}
            }).execute()
            
            if hasattr(response, 'error') and response.error:
                self.logger.error(f"Failed to send message to queue {self.options.name}: {response.error}")
                raise Exception(f"Failed to send message to queue: {response.error}")
            
            self.logger.info(f"Scheduled task for job '{self.options.name}'")
            
        except Exception as e:
            self.logger.error(f"Error scheduling task for job '{self.options.name}': {e}")
            raise
    
    async def turn_on(self) -> None:
        """Start the job worker."""
        if self._running:
            return
        
        self.logger.info(f"Starting worker for job '{self.options.name}'")
        self._running = True
        
        # Create worker task
        worker_task = asyncio.create_task(self._create_worker())
        self.workers[self.options.name] = worker_task
    
    async def turn_off(self) -> None:
        """Stop the job worker."""
        if not self._running:
            return
        
        self.logger.info(f"Stopping worker for job '{self.options.name}'")
        self._running = False
        
        # Cancel worker task
        if self.options.name in self.workers:
            worker_task = self.workers[self.options.name]
            worker_task.cancel()
            try:
                await worker_task
            except asyncio.CancelledError:
                pass
            del self.workers[self.options.name]
    
    async def _create_worker(self) -> None:
        """Create and run the worker."""
        self.logger.info(f"Starting worker for job '{self.options.name}'. QueueName: {self.options.name}")
        
        if not self.options.handler:
            self.logger.info(f"No handler for job '{self.options.name}'")
            return
        
        while self._running:
            try:
                # Read messages from queue
                response = self.supabase.schema('pgmq_public').rpc('read', {
                    'n': self.batch_size,  # quantity of messages to read
                    'queue_name': self.options.name,
                    'sleep_seconds': self.options.visibility_timeout_in_seconds
                }).execute()
                
                if hasattr(response, 'error') and response.error:
                    self.logger.error(f"Error reading from queue {self.options.name}: {response.error}")
                    await asyncio.sleep(self.poll_interval)
                    continue
                
                # Process messages
                messages = response.data or []
                for msg in messages:
                    if not self._running:
                        break
                    
                    self.logger.debug(f"Processing job '{self.options.name}' with id {msg['msg_id']}")
                    
                    try:
                        # Call handler with message data
                        result = await self.options.handler(TaskHandlerArgs(data=(msg['message']['data'])))
                        
                        # Handle result based on status
                        if result.status == 'error':
                            self.logger.error(f"Job failed '{self.options.name}' with id {msg['msg_id']}: {result.result_message}")
                            # Archive failed messages
                            await self._archive_message(msg['msg_id'])
                        elif result.status == 'cancelled':
                            self.logger.info(f"Job cancelled '{self.options.name}' with id {msg['msg_id']}")
                            # Delete cancelled messages
                            await self._delete_message(msg['msg_id'])
                        else:
                            # Success - delete message
                            await self._delete_message(msg['msg_id'])
                            self.logger.info(f"Job completed '{self.options.name}' with id {msg['msg_id']}")
                    
                    except Exception as e:
                        self.logger.error(f"Error processing job '{self.options.name}' with id {msg['msg_id']}: {e}")
                        # Archive failed messages
                        await self._archive_message(msg['msg_id'])
                
                # Wait before next poll (convert milliseconds to seconds)
                await asyncio.sleep(self.options.poll_interval_in_millis / 1000)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in worker for queue {self.options.name}: {e}")
                await asyncio.sleep(self.options.poll_interval_in_millis / 1000)
    
    async def _delete_message(self, message_id: str) -> None:
        """Delete a message from the queue."""
        try:
            response = self.supabase.schema('pgmq_public').rpc('delete', {
                'queue_name': self.options.name,
                'message_id': message_id
            }).execute()
            
            if hasattr(response, 'error') and response.error:
                self.logger.error(f"Error deleting message {message_id}: {response.error}")
        except Exception as e:
            self.logger.error(f"Error deleting message {message_id}: {e}")
    
    async def _archive_message(self, message_id: str) -> None:
        """Archive a message (move to archive queue)."""
        try:
            response = self.supabase.schema('pgmq_public').rpc('archive', {
                'queue_name': self.options.name,
                'message_id': message_id
            }).execute()
            
            if hasattr(response, 'error') and response.error:
                self.logger.error(f"Error archiving message {message_id}: {response.error}")
        except Exception as e:
            self.logger.error(f"Error archiving message {message_id}: {e}")
