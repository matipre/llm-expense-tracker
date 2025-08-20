"""
Supabase queue service implementation for the bot service.
Uses Supabase Queues (pgmq) for all queue operations.
"""
import asyncio
import logging
from datetime import datetime
from typing import Any, Callable

from supabase import Client

from domain.entities.message import IncomingMessage, BotResponse
from domain.interfaces.queue_service import IQueueService


class SupabaseQueueService(IQueueService):
    """Supabase queue service that uses Supabase Queues (pgmq) for all queue operations."""
    
    def __init__(self, supabase_client: Client):
        self.supabase: Client = supabase_client
        self.logger = logging.getLogger(__name__)
        self._running = False
        self._consumer_task = None
        
        self.logger.info("Supabase queue service initialized with injected client")
    
    async def consume_messages(self, callback: Callable[[IncomingMessage], Any]) -> None:
        """Consume messages from the Supabase queue."""
        try:
            await self._consume_from_supabase_queue(callback)
        except Exception as e:
            self.logger.error(f"Error consuming messages: {e}", exc_info=True)

    async def _consume_from_supabase_queue(self, callback: Callable[[IncomingMessage], Any]) -> None:
        """Consume messages from Supabase Queues (pgmq)."""
        try:
            # Read from telegram_received_messages queue
            response = self.supabase.schema('pgmq_public').rpc('read', {
                'n': 10,  # quantity of messages to read
                'queue_name': 'telegram_received_messages',
                'sleep_seconds': 30  # visibility timeout in seconds
            }).execute()
            
            # Check for errors in the response
            if hasattr(response, 'error') and response.error:
                self.logger.error(f"Error reading from Supabase queue: {response.error}")
                return
            
            # Process messages if any exist
            messages = response.data or []
            for msg in messages:
                try:
                    # Parse the message
                    payload = msg["message"]
                    message = IncomingMessage(
                        telegram_user_id=payload["telegramUserId"],
                        chat_id=payload["chatId"],
                        message_text=payload["messageText"],
                        timestamp=datetime.fromisoformat(payload["timestamp"].replace("Z", "")),
                        message_id=payload["messageId"]
                    )
                    
                    # Process the message
                    await callback(message)
                    
                    # Delete message after successful processing
                    delete_response = self.supabase.schema('pgmq_public').rpc('delete', {
                        'queue_name': 'telegram_received_messages',
                        'message_id': msg['msg_id']
                    }).execute()
                    
                    # Check if deletion was successful
                    if hasattr(delete_response, 'error') and delete_response.error:
                        self.logger.error(f"Error deleting message {msg['msg_id']}: {delete_response.error}")
                    else:
                        self.logger.info(f"Processed and deleted message {msg['msg_id']}")
                    
                except Exception as e:
                    self.logger.error(f"Error processing message {msg.get('msg_id', 'unknown')}: {e}", exc_info=True)
                    
        except Exception as e:
            self.logger.error(f"Error in _consume_from_supabase_queue: {e}", exc_info=True)


    
    async def send_response(self, response: BotResponse) -> None:
        """Send a response back to the connector service."""
        try:
            payload = {
                "chatId": response.chat_id,
                "text": response.text,
                "replyToMessageId": response.reply_to_message_id
            }
            
            await self._send_to_supabase_queue(payload)
            
            self.logger.info(f"Sent response to chat {response.chat_id}")
            
        except Exception as e:
            self.logger.error(f"Error sending response: {e}", exc_info=True)
            raise

    async def _send_to_supabase_queue(self, payload: dict) -> None:
        """Send response using Supabase Queues."""
        response = self.supabase.schema('pgmq_public').rpc('send', {
            'queue_name': 'telegram_bot_responses',
            'message': payload,
            'sleep_seconds': 30
        }).execute()
        
        # Check for errors in the response
        if hasattr(response, 'error') and response.error:
            self.logger.error(f"Error sending message to Supabase queue: {response.error}")
            raise Exception(f"Failed to send message to Supabase queue: {response.error}")
        
        if response.data is None:
            raise Exception("Failed to send message to Supabase queue: no data returned")


    
    async def start_consumer(self) -> None:
        """Start the message consumer."""
        if self._running:
            return
        
        self._running = True
        self.logger.info("Starting queue consumer")
        
        # Start the consumer loop
        self._consumer_task = asyncio.create_task(self._consumer_loop())
    
    async def stop_consumer(self) -> None:
        """Stop the message consumer."""
        self._running = False
        
        if self._consumer_task:
            self._consumer_task.cancel()
            try:
                await self._consumer_task
            except asyncio.CancelledError:
                pass
            
        self.logger.info("Stopped queue consumer")
    
    async def _consumer_loop(self) -> None:
        """Main consumer loop that polls for messages."""
        from ...application.services.message_processor import MessageProcessorService
        
        # This will be injected properly in the main app
        message_processor = None
        
        while self._running:
            try:
                if message_processor:
                    await self.consume_messages(message_processor.process_message)
                
                # Wait before next poll
                await asyncio.sleep(5)  # Poll every 5 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in consumer loop: {e}", exc_info=True)
                await asyncio.sleep(10)  # Wait longer on error
