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
        self.history = []
        agent=create_tool_calling_agent(self.llm,self.tools,self.chat_prompt)
        agent_executor=AgentExecutor(agent=agent,tools=self.tools,verbose=True)
        self.executor=agent_executor

    def _build_prompt(self):
        # System message: instructions for the LLM
        system_prompt = SystemMessagePromptTemplate.from_template(
            "You are a helpful AI assistant.\n"
            "You have access to some mathematical tools.\n"
            "make one tool call per operation\n"
            "Make sure you pass the correct json input to the function\n"
            "Always use the 'final_answer' tool exactly once at the end to provide the final result.\n"
            "Do not call any other tool after using 'final_answer'.\n"
            "pass the latest output to final answer tool and take its output and end the chain"
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
            # few_shot_prompt,
            history_intro,
            MessagesPlaceholder(variable_name="history"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
            user_prompt,
        ])


    def ask(self, query: str) -> str:
        """Send a query and return the final agent output."""
        result = self.executor.invoke({"question": query, "history": self.history})
        output = result["output"]

        self.history.append(HumanMessage(content=query))
        self.history.append(AIMessage(content=output))

        return output

if __name__=="__main__":
    bot=ChatBot()
    print(bot.ask("what model are you"))