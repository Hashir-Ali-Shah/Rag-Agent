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
from Streaming import QueueCallbackHandler
from DocReader import DocumentReader


from typing import List, Optional, Union, BinaryIO, TextIO
from pathlib import Path



class ChatBot():
    def __init__(self, temperature: float = 0.7):
        self.callback_handler = QueueCallbackHandler()
        self.document_reader = DocumentReader()
        self.tools=MathTools.get_tools()
        self.llm = ChatGroq(
            model="openai/gpt-oss-20b",
            temperature=temperature,
            api_key=API_KEY,
            streaming=True,
            callbacks=[self.callback_handler],
        )
        self.session=SessionMemoryManager
        self.chat_prompt = ChatBotPrompts.build_prompt()
        self.rag_pipeline = RAGPipeline()
        agent=create_tool_calling_agent(self.llm,self.tools,self.chat_prompt)
        agent_executor=AgentExecutor(agent=agent,tools=self.tools,verbose=False,callbacks=[self.callback_handler])
        self.executor=agent_executor
        self.pipeline=self.pipeline_config()
    
    def read(self, file_input: Union[str, BinaryIO, TextIO], 
            filename: Optional[str] = None, ) -> list[str]:
        """Read document from path and return list of text chunks."""
        file_path = os.path.abspath(file_input) if isinstance(file_input, str) else file_input
        if isinstance(file_input,str):
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}") 
        if filename:
            self.rag_pipeline.ingest(self.document_reader.read(file_path, filename))
        else:
            self.rag_pipeline.read(self.document_reader.read(file_path))

            # Use DocumentReader to read the file
        

    
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
    
    async def ask_stream(self, query: str, session_id: str = "default", k: int = 4):
        self.callback_handler.clear()
        async for event in self.pipeline.astream_events(
            {"question": query},
            config={"configurable": {"session_id": session_id, "k": k}},
            version="v1"
        ):
            if event["event"] == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                if chunk and chunk.content:

                    if isinstance(chunk.content, list):
                        yield "".join(chunk.content)
                    else:
                        yield chunk.content





if __name__ == "__main__":
    import asyncio

    
    async def test_streaming():
        bot = ChatBot()
        print("Streaming result:")
        async for token in bot.ask_stream("hello", session_id="test_session", k=3):
            print(token, end="", flush=True)
        print()  # New line at end
    # Test direct LLM streaming (bypass agent)
    
    asyncio.run(test_streaming())


