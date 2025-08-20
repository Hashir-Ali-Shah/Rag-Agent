import os
from dotenv import load_dotenv
import asyncio
# Load variables from .env file
load_dotenv()

# Get your API key
API_KEY = os.getenv("GROQ_API_KEY")


from langchain_groq import ChatGroq
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.runnables import ConfigurableFieldSpec
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.schema.runnable import RunnableLambda,RunnablePassthrough

from SessionManager import SessionMemoryManager
from Tools import MathTools
from Prompts import ChatBotPrompts
from Rag import RAGPipeline




class ChatBot():
    def __init__(self, temperature: float = 0.7):
        self.tools=MathTools.get_tools()
        self.llm = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=temperature,
            api_key=API_KEY,
            streaming=True,
        )
        self.session=SessionMemoryManager
        self.chat_prompt = ChatBotPrompts.build_prompt()
        self.rag_pipeline = RAGPipeline()
        agent=create_tool_calling_agent(self.llm,self.tools,self.chat_prompt)
        agent_executor=AgentExecutor(agent=agent,tools=self.tools,verbose=True)
        self.executor=agent_executor
        self.pipeline=self.pipeline_config()

    
    def pipeline_config(self):
        pipeline = RunnableWithMessageHistory(
        runnable=RunnableLambda(self.rag_pipeline._retrieve_context) | self.executor,                  # your AgentExecutor
        get_session_history=self.session.get_session,  # session-based memory factory
        input_messages_key="question",           # matches prompt variable
        history_messages_key="chat_history",     # matches placeholder in prompt
        history_factory_config=[
            ConfigurableFieldSpec(
                id="session_id",
                annotation=str,
                name="Session ID",
                description="The session ID to use for chat history",
                default="id_default",
            ),
            ConfigurableFieldSpec(
                id="k",
                annotation=int,
                name="k",
                description="Number of messages to keep in memory",
                default=3,
            )
        ]
    )
        return pipeline

    async def ask(self, query: str,session_id:str="default",k:int=4) -> str:
        """Send a query and return the final agent output."""
 
        result =await  self.pipeline.ainvoke({"question": query},config={"configurable":{"session_id": session_id,"k":k}} )
        return result["output"]

if __name__ == "__main__":
    bot = ChatBot()
    result = asyncio.run(bot.ask("solve 2+2 use final answer tool in the end ", session_id="test_session", k=3))
    print(result)



