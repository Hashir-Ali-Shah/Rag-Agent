from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_openai_functions_agent,create_tool_calling_agent
from langchain_core.prompts import (
    ChatPromptTemplate,MessagesPlaceholder)

import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Get your API key
API_KEY = os.getenv("GROQ_API_KEY")

from Tools import MathTools
# ---- Simple Tool ----
@tool
def add_numbers(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


@tool
def subtract_numbers(a: int, b: int) -> int:
    """Subtract b from a."""
    return a - b

@tool
def multiply_numbers(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

@tool
def divide_numbers(a: int, b: int) -> float:
    """Divide a by b. Returns float. Raises error if b is 0."""
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b
@tool
def final_answer(answer: str) -> str:
    """Use this tool to give the final answer to the user. 
    Always call this at the end instead of repeating other tools."""
    return answer


tools = MathTools.get_tools()

# ---- Init LLM ----
llm = ChatGroq(
    model="llama3-70b-8192",
    temperature=0,
    api_key=API_KEY,
)

# ---- Build Agent ----
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Use the tools if needed. always call the final answer tool in end "),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])
agent = create_tool_calling_agent(llm, tools, prompt)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# ---- Test Call ----
print(agent_executor.invoke({"input": "What is 1+2?"}))
