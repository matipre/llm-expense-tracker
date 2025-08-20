"""
Job factory interfaces for the bot service.
Mirrors the TypeScript implementation for consistency.
"""
from abc import ABC, abstractmethod
from typing import Any, Protocol
from dataclasses import dataclass


@dataclass
class TaskHandlerArgs:
    """Arguments passed to task handlers."""
    data: Any


@dataclass
class TaskHandlerResult:
    """Result returned by task handlers."""
    status: str  # 'success' | 'error' | 'cancelled'
    result_message: str = None


class JobOptions:
    """Options for creating a job."""
    def __init__(self, name: str, handler=None, poll_interval_in_millis: int = 1000, visibility_timeout_in_seconds: int = 5):
        self.name = name
        self.handler = handler
        self.poll_interval_in_millis = poll_interval_in_millis
        self.visibility_timeout_in_seconds = visibility_timeout_in_seconds


class Job(ABC):
    """Interface for job operations."""
    
    @abstractmethod
    async def schedule_task(self, data: Any) -> None:
        """Schedule a task with the given data."""
        pass
    
    @abstractmethod
    async def turn_on(self) -> None:
        """Start the job worker."""
        pass
    
    @abstractmethod
    async def turn_off(self) -> None:
        """Stop the job worker."""
        pass


class JobFactory(ABC):
    """Interface for creating jobs."""
    
    @abstractmethod
    def create_job(self, options: JobOptions) -> Job:
        """Create a job with the given options."""
        pass
