from fastapi import FastAPI, Form, File, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from ChatBot import ChatBot
import json
from typing import List, Optional
import asyncio

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_methods=["*"],
    allow_headers=["*"],
)


chatbot_cache = {}

def get_or_create_chatbot(chat_id: str) -> ChatBot:
    """
    Get existing ChatBot instance from cache or create a new one.
    """
    if chat_id not in chatbot_cache:
        print(f"[{chat_id}] Creating new ChatBot instance")
        chatbot_cache[chat_id] = ChatBot()
    else:
        print(f"[{chat_id}] Using existing ChatBot instance")
    
    return chatbot_cache[chat_id]

@app.post("/chat")
async def chat_endpoint(
    chat_id: str = Form(...),
    message: str = Form(...),
    files: Optional[List[UploadFile]] = File(None)
):
    """
    HTTP endpoint for chat functionality.
    Receives chat_id, message, and optional files.
    Returns streaming response.
    """
    print(f"[{chat_id}] Received message: {message}")
    

    chatbot = get_or_create_chatbot(chat_id)
    
    try:
  
        if files:
            for file in files:
                if file.filename:
                    print(f"[{chat_id}] Processing file: {file.filename}")
        
                    try:
                        print(file.file)
                        chatbot.read(file.file,filename= file.filename)
                    except Exception as file_error:
                        print(f"[{chat_id}] Error reading file {file.filename}: {file_error}")
        

        async def generate_response():
            print(f"[{chat_id}] Processing message for chat_id: {chat_id}")
            

            buffer = ""
            async for token in chatbot.ask_stream(message, session_id=chat_id, k=3):
                    
                    buffer += token
                    if token in {".", "!", "?", " "}:
                        yield buffer
                        buffer = ""
            if buffer:  
                    yield buffer
    
   
        return StreamingResponse(
            generate_response(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no", 
            }
        )
        
    except Exception as e:
        print(f"[{chat_id}] Error processing request: {e}")
        
        async def error_response():
            yield f"Error: {str(e)}"
        
        return StreamingResponse(
            error_response(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache"}
        )