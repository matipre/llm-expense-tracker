"""
Expense tool interface for LangChain tools.
"""

from abc import ABC, abstractmethod
from langchain.tools import BaseTool


class IExpenseTool(ABC):
    """Interface for expense-related LangChain tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the tool name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Get the tool description with usage guidelines."""
        pass

    @abstractmethod
    def get_langchain_tool(self) -> BaseTool:
        """Get the LangChain BaseTool instance."""
        pass
