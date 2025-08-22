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
    allow_origins=["*"],  # or list your frontend domains
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache ChatBot instances: id -> ChatBot instance
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
    
    # Get or create ChatBot instance for this chat_id
    chatbot = get_or_create_chatbot(chat_id)
    
    try:
        # Process files if any
        if files:
            for file in files:
                if file.filename:
                    print(f"[{chat_id}] Processing file: {file.filename}")
                    # Pass file object and filename to chatbot
                    try:
                        print(file.file)
                        chatbot.read(file.file,filename= file.filename)
                    except Exception as file_error:
                        print(f"[{chat_id}] Error reading file {file.filename}: {file_error}")
        
        # Process the message and get streaming response
        async def generate_response():
            print(f"[{chat_id}] Processing message for chat_id: {chat_id}")
            
            # Replace this with your actual chatbot response generation
            # This is a placeholder for streaming response
          
            
            # Simulate streaming by yielding chunks
            buffer = ""
            async for token in chatbot.ask_stream(message, session_id=chat_id, k=3):
                    
                    buffer += token
                    if token in {".", "!", "?", " "}:
                        yield buffer
                        buffer = ""
            if buffer:  # flush remainder
                    yield buffer
    
        # Return streaming response
        return StreamingResponse(
            generate_response(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Needed for nginx
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