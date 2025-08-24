"""
Add expense tool for LangChain.
"""

from datetime import datetime
from decimal import Decimal

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from domain.entities.expense import Expense
from domain.interfaces.expense_categories_repository import IExpenseCategoriesRepository
from domain.interfaces.expense_repository import IExpenseRepository
from domain.interfaces.expense_tool import IExpenseTool


class AddExpenseInput(BaseModel):
    """Input schema for add_expense tool."""
    description: str = Field(description="What the expense was for")
    amount: float = Field(description="Amount spent (positive number)")
    category: str = Field(description="Expense category (will be validated)")


class AddExpenseToolImpl(BaseTool):
    """LangChain BaseTool implementation for adding expenses."""
    
    name: str = "add_expense"
    description: str = """Add a new expense when user mentions spending money.

Use this tool when users:
- Mention buying something: 'coffee $5', 'pizza for lunch 20 bucks', 'bought groceries 89'
- State past purchases: 'spent $50 on gas', 'paid 23 for uber', 'dinner cost 45'
- Use expense language with amounts: 'cost', 'paid', 'bought', 'spent' + dollar amounts
- Provide expense details: description and amount (category will be determined from available options)

Examples:
- 'coffee $5' → add_expense(description='coffee', amount=5.0, category='Food')
- 'spent $50 on gas' → add_expense(description='gas', amount=50.0, category='Transportation')
- 'bought groceries for 89 dollars' → add_expense(description='groceries', amount=89.0, category='Food')"""
    
    args_schema: type[BaseModel] = AddExpenseInput
    
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
    
    def _run(self, description: str, amount: float, category: str) -> str:
        """Synchronous run method (not used in async context)."""
        raise NotImplementedError("Use arun instead")
    
    async def _arun(self, description: str, amount: float, category: str) -> str:
        """Add an expense and return confirmation."""
        try:
            # Validate category
            if not await self.categories_repository.is_valid_category(category):
                categories = await self.categories_repository.get_all_categories()
                return f"Invalid category '{category}'. Must be one of: {', '.join(categories)}"
            
            # Create and save expense
            expense = Expense(
                id=None,
                user_id=self.user_id,
                description=description,
                amount=Decimal(str(amount)),
                category=category,
                added_at=datetime.utcnow(),
            )
            
            saved_expense = await self.expense_repository.create(expense)
            return f"✅ Added {category} expense: {description} - ${saved_expense.amount}"
            
        except Exception as e:
            return f"❌ Error adding expense: {str(e)}"


class AddExpenseTool(IExpenseTool):
    """Add expense tool implementation."""

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
        return "add_expense"

    @property
    def description(self) -> str:
        """Get the tool description with usage guidelines."""
        return """Add a new expense when user mentions spending money.

Use this tool when users:
- Mention buying something: 'coffee $5', 'pizza for lunch 20 bucks', 'bought groceries 89'
- State past purchases: 'spent $50 on gas', 'paid 23 for uber', 'dinner cost 45'
- Use expense language with amounts: 'cost', 'paid', 'bought', 'spent' + dollar amounts
- Provide expense details: description and amount (category will be determined from available options)

Examples:
- 'coffee $5' → add_expense(description='coffee', amount=5.0, category='Food')
- 'spent $50 on gas' → add_expense(description='gas', amount=50.0, category='Transportation')
- 'bought groceries for 89 dollars' → add_expense(description='groceries', amount=89.0, category='Food')"""

    def get_langchain_tool(self) -> BaseTool:
        """Get the LangChain BaseTool instance."""
        return AddExpenseToolImpl(
            self.expense_repository,
            self.categories_repository,
            self.user_id
        )
