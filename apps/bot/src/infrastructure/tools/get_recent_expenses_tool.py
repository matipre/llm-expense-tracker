"""
Get recent expenses tool for LangChain.
"""

from datetime import datetime, timedelta
from decimal import Decimal

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from domain.interfaces.expense_repository import IExpenseRepository
from domain.interfaces.expense_tool import IExpenseTool


class GetRecentExpensesInput(BaseModel):
    """Input schema for get_recent_expenses tool."""
    days: int = Field(description="Number of days to look back", default=30)


class GetRecentExpensesToolImpl(BaseTool):
    """LangChain BaseTool implementation for getting recent expenses."""
    
    name: str = "get_recent_expenses"
    description: str = """Get user's recent expenses and spending summaries.

Use this tool when users ask about:
- Recent spending: 'what did I spend?', 'show my expenses', 'my spending', 'expense report'
- Time-based queries: 'expenses this month', 'recent purchases', 'last 30 days', 'this week'
- General summaries: 'how much have I spent?', 'spending summary', 'expense totals'
- Comparative queries: 'spending last week vs this week', 'monthly expenses'

Examples:
- 'show my expenses' → get_recent_expenses(days=30)
- 'what did I spend last week?' → get_recent_expenses(days=7) 
- 'expenses this month' → get_recent_expenses(days=30)
- 'recent spending' → get_recent_expenses(days=30)"""
    
    args_schema: type[BaseModel] = GetRecentExpensesInput
    
    def __init__(self, expense_repository: IExpenseRepository, user_id: int):
        super().__init__()
        # Use object.__setattr__ to bypass Pydantic's field validation
        object.__setattr__(self, 'expense_repository', expense_repository)
        object.__setattr__(self, 'user_id', user_id)
    
    def _run(self, days: int = 30) -> str:
        """Synchronous run method (not used in async context)."""
        raise NotImplementedError("Use arun instead")
    
    async def _arun(self, days: int = 30) -> str:
        """Get recent expenses and return formatted summary."""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            expenses = await self.expense_repository.find_by_user_id_and_date_range(
                self.user_id, start_date, end_date
            )
            
            if not expenses:
                period = "today" if days == 1 else f"last {days} days"
                return f"No expenses found for {period}."
            
            total = sum(expense.amount for expense in expenses)
            
            # Group by category
            by_category = {}
            for expense in expenses:
                if expense.category not in by_category:
                    by_category[expense.category] = Decimal('0')
                by_category[expense.category] += expense.amount
            
            # Format response
            period = "today" if days == 1 else f"last {days} days"
            response = f"💰 Your expenses for {period}:\n\n"
            response += f"**Total: ${total}**\n\n"
            
            if by_category:
                response += "**By Category:**\n"
                for category, amount in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
                    response += f"• {category}: ${amount}\n"
                response += "\n"
            
            response += "**Recent Expenses:**\n"
            for expense in expenses[:10]:  # Show last 10
                response += f"• {expense.description} - ${expense.amount} ({expense.category})\n"
            
            if len(expenses) > 10:
                response += f"\n... and {len(expenses) - 10} more"
            
            return response
            
        except Exception as e:
            return f"❌ Error retrieving expenses: {str(e)}"


class GetRecentExpensesTool(IExpenseTool):
    """Get recent expenses tool implementation."""

    def __init__(self, expense_repository: IExpenseRepository, user_id: int):
        self.expense_repository = expense_repository
        self.user_id = user_id

    @property
    def name(self) -> str:
        """Get the tool name."""
        return "get_recent_expenses"

    @property
    def description(self) -> str:
        """Get the tool description with usage guidelines."""
        return """Get user's recent expenses and spending summaries.

Use this tool when users ask about:
- Recent spending: 'what did I spend?', 'show my expenses', 'my spending', 'expense report'
- Time-based queries: 'expenses this month', 'recent purchases', 'last 30 days', 'this week'
- General summaries: 'how much have I spent?', 'spending summary', 'expense totals'
- Comparative queries: 'spending last week vs this week', 'monthly expenses'

Examples:
- 'show my expenses' → get_recent_expenses(days=30)
- 'what did I spend last week?' → get_recent_expenses(days=7) 
- 'expenses this month' → get_recent_expenses(days=30)
- 'recent spending' → get_recent_expenses(days=30)"""

    def get_langchain_tool(self) -> BaseTool:
        """Get the LangChain BaseTool instance."""
        return GetRecentExpensesToolImpl(self.expense_repository, self.user_id)
