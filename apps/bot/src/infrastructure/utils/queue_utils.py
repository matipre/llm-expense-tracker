"""
Queue utility functions for creating task handler results.
"""

from domain.interfaces.job_factory import TaskHandlerResult


def create_success_result(message: str = "Task completed successfully") -> TaskHandlerResult:
    """Create a success result."""
    return TaskHandlerResult(
        status="success",
        result_message=message
    )


def create_error_result(message: str) -> TaskHandlerResult:
    """Create an error result."""
    return TaskHandlerResult(
        status="error",
        result_message=message
    )


def create_cancelled_result(message: str = "Task was cancelled") -> TaskHandlerResult:
    """Create a cancelled result."""
    return TaskHandlerResult(
        status="cancelled",
        result_message=message
    )