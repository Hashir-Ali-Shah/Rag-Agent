import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Get your API key
API_KEY = os.getenv("GROQ_API_KEY")


from langchain_groq import ChatGroq
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
    FewShotChatMessagePromptTemplate,
    MessagesPlaceholder
)
from langchain_core.messages import HumanMessage, AIMessage
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.memory import ConversationBufferWindowMemory
from Tools import MathTools




class ChatBot(MathTools):
    def __init__(self, temperature: float = 0.7):
        self.tools=self.get_tools()
        self.llm = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=temperature,
            api_key=API_KEY,
            streaming=True,
        )
    
        self.chat_prompt = self._build_prompt()
        self.memory = ConversationBufferWindowMemory(k=3, return_messages=True,memory_key="chat_history")
        agent=create_tool_calling_agent(self.llm,self.tools,self.chat_prompt)
        agent_executor=AgentExecutor(agent=agent,tools=self.tools,verbose=True,memory=self.memory)
        self.executor=agent_executor

    def _build_prompt(self):
        # System message: instructions for the LLM
        system_prompt = SystemMessagePromptTemplate.from_template(
            "You are a helpful AI assistant.\n"
        "You're a helpful assistant. When answering a user's question "
        "you should first use one of the tools provided. After using a "
        "tool the tool output will be provided in the "
        "'scratchpad' below. If you have an answer in the "
        "scratchpad you should  use final answer tool to answer the user "
        "Final answer tool should be called at the end of the conversation only once"
        )

        # Optional examples (few-shot)
        examples = [
            {
                "input": "What is 2 + 3?",
                "output": "Use add_numbers tool to compute 2 + 3, then call the  the final answer tool with output."
            },
            {
                "input": "What is 10 * 5?",
                "output": "Use multiply_numbers tool to compute 10 * 5, then call the final answer tool with output."
            },
                        {
                "input": "tell me about langchain?",
                "output": "no relevant tools available for this question, so using final answer tool to answer the user."
            },
        ]

        # Few-shot example template
        example_prompt = ChatPromptTemplate.from_messages([
            HumanMessagePromptTemplate.from_template("{input}"),
            AIMessagePromptTemplate.from_template("{output}")
        ])

        few_shot_prompt = FewShotChatMessagePromptTemplate(
            example_prompt=example_prompt,
            examples=examples
        )

        # User prompt
        user_prompt = HumanMessagePromptTemplate.from_template("{question}")

        # Chat history placeholder
        history_intro = SystemMessagePromptTemplate.from_template("Below is the chat history:")

        # Combine everything
        return ChatPromptTemplate.from_messages([
            system_prompt,
            few_shot_prompt,
            history_intro,
            MessagesPlaceholder(variable_name="chat_history"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
            user_prompt,
        ])


    def ask(self, query: str) -> str:
        """Send a query and return the final agent output."""
        result = self.executor.invoke({"question": query})
        return result["output"]

if __name__=="__main__":
    bot=ChatBot()
    print(bot.ask("my name is hashir"))
    print(bot.ask("What is my name?"))