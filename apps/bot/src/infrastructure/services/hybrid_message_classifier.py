"""
Hybrid message classifier that combines rule-based filtering with lightweight LLM classification.
"""

import logging
import re
from typing import Set

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from domain.interfaces.message_classifier import IMessageClassifier


class HybridMessageClassifier(IMessageClassifier):
    """
    Hybrid classifier that uses rule-based filtering for obvious cases 
    and lightweight LLM for borderline messages.
    """

    def __init__(self, openai_api_key: str, model: str = "gpt-3.5-turbo"):
        self.llm = ChatOpenAI(
            api_key=openai_api_key,
            model=model,
            temperature=0.0,  # Deterministic for classification
        )
        self.logger = logging.getLogger(__name__)
        
        # Rule-based patterns for obvious expense messages  
        self.expense_patterns = {
            # Money amounts
            r'\$\d+\.?\d*|\d+\.?\d*\s*(dollars?|bucks?|usd)',
            # Expense verbs with amounts
            r'\b(spent|paid|bought|cost|costs|purchase|expenses?)\b.*\$?\d+',
            # Common expense contexts
            r'\b(coffee|lunch|dinner|gas|groceries|uber|taxi|shopping)\b.*\$?\d+',
            # Transaction language
            r'\b(receipt|transaction|bill|invoice)\b',
        }
        
        # Compile regex patterns
        self.compiled_expense = [re.compile(pattern, re.IGNORECASE) 
                               for pattern in self.expense_patterns]

    async def is_expense_related(self, message_text: str) -> bool:
        """
        Classify message using hybrid approach:
        1. Rule-based classification for obvious cases
        2. LLM classification for borderline messages
        """
        message_text = message_text.strip()
        
        if not message_text:
            return False
            
        # First, check rule-based patterns for obvious cases
        rule_result = self._classify_with_rules(message_text)
        
        if rule_result is True:
            self.logger.info(
                "Rule-based classification: %s -> %s", 
                message_text[:50], rule_result
            )
            return True
            
        # For borderline cases, use lightweight LLM classification
        try:
            llm_result = await self._classify_with_llm(message_text)
            self.logger.info(
                "LLM classification: %s -> %s", 
                message_text[:50], llm_result
            )
            return llm_result
        except Exception as e:
            self.logger.error("LLM classification failed: %s", e)
            # Default to processing the message if classification fails
            return True

    def _classify_with_rules(self, message_text: str) -> bool:
        """
        Use rule-based patterns to classify obvious cases.
        Returns None if patterns are inconclusive.
        """
        # Check for obvious expense patterns first
        for pattern in self.compiled_expense:
            if pattern.search(message_text):
                return True
                
        return False

    async def _classify_with_llm(self, message_text: str) -> bool:
        """Use lightweight LLM to classify borderline messages."""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a message classifier for an expense tracking bot.

Your job is to determine if a message is related to expenses or not.

Expense-related messages include:
- Mentions of spending money, purchases, costs, bills
- Adding expenses or transactions
- Asking about past expenses or spending summaries  
- Financial transactions of any kind

Non-expense messages include:
- General greetings and casual conversation
- Questions unrelated to money/expenses
- Commands or requests not about finances
- Small talk or social interaction

Respond with only "YES" if the message is expense-related, or "NO" if it's not."""),
            ("human", "{message}")
        ])
        
        chain = prompt | self.llm
        result = await chain.ainvoke({"message": message_text})
        
        response = result.content.strip().upper()
        return response == "YES"
