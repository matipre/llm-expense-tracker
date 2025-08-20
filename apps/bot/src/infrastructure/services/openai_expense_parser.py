"""
OpenAI expense parser implementation using LangChain.
"""
import json
import logging
from decimal import Decimal
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from domain.entities.expense import EXPENSE_CATEGORIES
from domain.entities.message import ParsedExpense
from domain.interfaces.expense_parser import IExpenseParser


class OpenAIExpenseParser(IExpenseParser):
    """OpenAI-based expense parser using LangChain."""
    
    def __init__(self, openai_api_key: str, model: str = "gpt-3.5-turbo"):
        self.llm = ChatOpenAI(
            api_key=openai_api_key,
            model=model,
            temperature=0.1  # Low temperature for consistent parsing
        )
        self.logger = logging.getLogger(__name__)
        
        # System prompt for expense parsing
        self.expense_parse_prompt = f"""You are an expense tracking assistant. Your job is to parse user messages and extract expense information.

User messages may contain:
- A description of what they spent money on
- An amount (which could be in various formats like "20", "$20", "20 bucks", "twenty dollars", etc.)
- Sometimes a category hint

You must categorize expenses into one of these categories:
{', '.join(EXPENSE_CATEGORIES)}

Respond with a JSON object containing:
- "is_expense": boolean (true if this is an expense-related message)
- "description": string (what the expense was for, cleaned up)
- "amount": number (the numeric amount, positive or negative)
- "category": string (one of the valid categories)
- "confidence": number (0.0-1.0, how confident you are this is correct)

If the message is not about an expense (like greetings, questions, etc.), set "is_expense" to false.

Examples:
- "Pizza 20 bucks" -> {{"is_expense": true, "description": "Pizza", "amount": 20, "category": "Food", "confidence": 0.9}}
- "Spent $50 on gas" -> {{"is_expense": true, "description": "Gas", "amount": 50, "category": "Transportation", "confidence": 0.9}}
- "Hello" -> {{"is_expense": false, "description": "", "amount": 0, "category": "", "confidence": 0}}
"""

    async def parse_expense(self, message_text: str) -> Optional[ParsedExpense]:
        """Parse expense information from message text."""
        try:
            self.logger.info(f"Parsing expense from message: {message_text}")
            
            messages = [
                SystemMessage(content=self.expense_parse_prompt),
                HumanMessage(content=message_text)
            ]
            
            response = await self.llm.ainvoke(messages)
            result = json.loads(response.content)
            
            if not result.get("is_expense", False):
                self.logger.info("Message is not an expense")
                return None
            
            # Validate required fields
            if not all(key in result for key in ["description", "amount", "category", "confidence"]):
                self.logger.warning(f"Missing required fields in LLM response: {result}")
                return None
            
            # Validate category
            if result["category"] not in EXPENSE_CATEGORIES:
                self.logger.warning(f"Invalid category from LLM: {result['category']}")
                result["category"] = "Other"
            
            parsed_expense = ParsedExpense(
                description=result["description"],
                amount=Decimal(str(result["amount"])),
                category=result["category"],
                confidence_score=float(result["confidence"])
            )
            
            self.logger.info(f"Parsed expense: {parsed_expense}")
            return parsed_expense
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response from LLM: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error parsing expense: {e}", exc_info=True)
            return None
    
    async def is_expense_message(self, message_text: str) -> bool:
        """Determine if a message contains expense information."""
        try:
            # First, do a quick check with a simpler prompt
            simple_prompt = """Is this message about spending money or an expense? 
            
Respond with just "YES" or "NO".

Examples:
- "Pizza 20 bucks" -> YES
- "Hello" -> NO
- "Bought coffee for $5" -> YES
- "How are you?" -> NO
"""
            
            messages = [
                SystemMessage(content=simple_prompt),
                HumanMessage(content=message_text)
            ]
            
            response = await self.llm.ainvoke(messages)
            result = response.content.strip().upper()
            
            is_expense = result == "YES"
            self.logger.info(f"Is expense message '{message_text}': {is_expense}")
            
            return is_expense
            
        except Exception as e:
            self.logger.error(f"Error checking if message is expense: {e}", exc_info=True)
            # Default to True to be safe - we'll catch parsing errors later
            return True
