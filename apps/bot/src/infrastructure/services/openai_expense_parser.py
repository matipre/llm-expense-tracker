"""
OpenAI expense parser implementation using LangChain with dependency injection.
"""

import logging

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from domain.entities.message import ProcessingResult
from domain.interfaces.expense_categories_repository import IExpenseCategoriesRepository
from domain.interfaces.expense_parser import IExpenseParser
from domain.interfaces.expense_tool import IExpenseTool


class OpenAIExpenseParser(IExpenseParser):
    """OpenAI-based expense parser using LangChain tools with dependency injection."""

    def __init__(
        self, 
        openai_api_key: str, 
        categories_repository: IExpenseCategoriesRepository,
        tools: list[IExpenseTool],
        model: str = "gpt-3.5-turbo"
    ):
        self.llm = ChatOpenAI(
            api_key=openai_api_key,
            model=model,
            temperature=0.1,
        )
        self.categories_repository = categories_repository
        self.tools = tools
        self.logger = logging.getLogger(__name__)

    async def process_message(self, message_text: str, user_id: int) -> ProcessingResult:
        """Process a message using LLM with tools."""
        try:
            self.logger.info("Processing message for user %s: %s", user_id, message_text)
            
            # Get available categories for system prompt
            categories = await self.categories_repository.get_all_categories()
            
            # Get LangChain tools from our tool implementations
            langchain_tools = [tool.get_langchain_tool() for tool in self.tools]
            
            # Create the system prompt
            system_prompt = f"""You are a helpful expense tracking assistant. 

Available expense categories: {', '.join(categories)}

Be conversational and friendly. When expenses are added successfully, acknowledge them positively. 
When providing summaries, format them clearly with totals and categories.

Use the available tools to help users track and query their expenses. The tools have detailed 
descriptions that will guide you on when to use each one."""

            # Create prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])
            
            # Create agent
            agent = create_openai_functions_agent(self.llm, langchain_tools, prompt)
            agent_executor = AgentExecutor(agent=agent, tools=langchain_tools, verbose=True)
            
            # Execute the agent
            result = await agent_executor.ainvoke({"input": message_text})
            response_text = result["output"]
            
            return ProcessingResult(
                success=True,
                response_text=response_text,
                summary_data=None,
            )
            
        except Exception as e:
            self.logger.error("Error processing message: %s", e, exc_info=True)
            return ProcessingResult(
                success=False,
                response_text="Sorry, I encountered an error processing your message. Please try again.",
                summary_data=None,
            )