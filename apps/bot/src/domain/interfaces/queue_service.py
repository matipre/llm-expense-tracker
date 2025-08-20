"""
Queue service interface.
"""
from abc import ABC, abstractmethod
from typing import Any, Callable

from domain.entities.message import IncomingMessage, BotResponse


class IQueueService(ABC):
    """Interface for queue service operations."""
    
    @abstractmethod
    async def consume_messages(self, callback: Callable[[IncomingMessage], Any]) -> None:
        """
        Start consuming messages from the queue.
        
        Args:
            callback: Function to call for each received message
        """
        pass
    
    @abstractmethod
    async def send_response(self, response: BotResponse) -> None:
        """
        Send a response back to the connector service.
        
        Args:
            response: The bot response to send
        """
        pass
    
    @abstractmethod
    async def start_consumer(self) -> None:
        """Start the message consumer."""
        pass
    
    @abstractmethod
    async def stop_consumer(self) -> None:
        """Stop the message consumer."""
        pass
