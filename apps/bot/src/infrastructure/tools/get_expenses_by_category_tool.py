"""
Get expenses by category tool for LangChain.
"""

from datetime import datetime, timedelta

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from domain.interfaces.expense_categories_repository import IExpenseCategoriesRepository
from domain.interfaces.expense_repository import IExpenseRepository
from domain.interfaces.expense_tool import IExpenseTool


class GetExpensesByCategoryInput(BaseModel):
    """Input schema for get_expenses_by_category tool."""
    category: str = Field(description="Expense category to filter by")
    days: int = Field(description="Number of days to look back", default=30)


class GetExpensesByCategoryToolImpl(BaseTool):
    """LangChain BaseTool implementation for getting expenses by category."""
    
    name: str = "get_expenses_by_category"
    description: str = """Get expenses filtered by a specific category.

Use this tool when users ask about spending in a specific category:
- Category-specific queries: 'how much on food?', 'transportation costs', 'housing expenses'
- Category spending patterns: 'food spending this month', 'entertainment budget', 'medical costs'
- Category comparisons: 'food vs entertainment', 'utilities this month'
- Category analysis: 'biggest food expenses', 'transportation breakdown'

Available categories: Food, Transportation, Housing, Utilities, Insurance, Medical/Healthcare, 
Savings, Debt, Education, Entertainment, Other

Examples:
- 'how much on food this month?' → get_expenses_by_category(category='Food', days=30)
- 'transportation costs last week' → get_expenses_by_category(category='Transportation', days=7)
- 'entertainment spending' → get_expenses_by_category(category='Entertainment', days=30)"""
    
    args_schema: type[BaseModel] = GetExpensesByCategoryInput
    
    def __init__(
        self, 
        expense_repository: IExpenseRepository, 
        categories_repository: IExpenseCategoriesRepository,
        user_id: int
    ):
        super().__init__()
        # Use object.__setattr__ to bypass Pydantic's field validation
        object.__setattr__(self, 'expense_repository', expense_repository)
        object.__setattr__(self, 'categories_repository', categories_repository)
        object.__setattr__(self, 'user_id', user_id)
    
    def _run(self, category: str, days: int = 30) -> str:
        """Synchronous run method (not used in async context)."""
        raise NotImplementedError("Use arun instead")
    
    async def _arun(self, category: str, days: int = 30) -> str:
        """Get expenses by category and return formatted summary."""
        try:
            # Validate category
            if not await self.categories_repository.is_valid_category(category):
                categories = await self.categories_repository.get_all_categories()
                return f"Invalid category '{category}'. Must be one of: {', '.join(categories)}"
            
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            all_expenses = await self.expense_repository.find_by_user_id_and_date_range(
                self.user_id, start_date, end_date
            )
            
            # Filter by category
            expenses = [e for e in all_expenses if e.category == category]
            
            if not expenses:
                period = "today" if days == 1 else f"last {days} days"
                return f"No {category} expenses found for {period}."
            
            total = sum(expense.amount for expense in expenses)
            period = "today" if days == 1 else f"last {days} days"
            
            response = f"💳 Your {category} expenses for {period}:\n\n"
            response += f"**Total: ${total}**\n\n"
            response += "**Expenses:**\n"
            
            for expense in expenses[:20]:  # Show up to 20
                response += f"• {expense.description} - ${expense.amount}\n"
            
            if len(expenses) > 20:
                response += f"\n... and {len(expenses) - 20} more"
            
            return response
            
        except Exception as e:
            return f"❌ Error retrieving {category} expenses: {str(e)}"


class GetExpensesByCategoryTool(IExpenseTool):
    """Get expenses by category tool implementation."""

    def __init__(
        self, 
        expense_repository: IExpenseRepository, 
        categories_repository: IExpenseCategoriesRepository,
        user_id: int
    ):
        self.expense_repository = expense_repository
        self.categories_repository = categories_repository
        self.user_id = user_id

    @property
    def name(self) -> str:
        """Get the tool name."""
        return "get_expenses_by_category"

    @property 
    def description(self) -> str:
        """Get the tool description with usage guidelines."""
        return """Get expenses filtered by a specific category.

Use this tool when users ask about spending in a specific category:
- Category-specific queries: 'how much on food?', 'transportation costs', 'housing expenses'
- Category spending patterns: 'food spending this month', 'entertainment budget', 'medical costs'
- Category comparisons: 'food vs entertainment', 'utilities this month'
- Category analysis: 'biggest food expenses', 'transportation breakdown'

Available categories: Food, Transportation, Housing, Utilities, Insurance, Medical/Healthcare, 
Savings, Debt, Education, Entertainment, Other

Examples:
- 'how much on food this month?' → get_expenses_by_category(category='Food', days=30)
- 'transportation costs last week' → get_expenses_by_category(category='Transportation', days=7)
- 'entertainment spending' → get_expenses_by_category(category='Entertainment', days=30)"""

    def get_langchain_tool(self) -> BaseTool:
        """Get the LangChain BaseTool instance."""
        return GetExpensesByCategoryToolImpl(
            self.expense_repository,
            self.categories_repository,
            self.user_id
        )
