from fastapi import FastAPI, Form, File,Query, UploadFile,WebSocket,WebSocketDisconnect,WebSocketException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from ChatBot import ChatBot
import json
from typing import List, Optional
import asyncio
import io
from VoiceAgent import VoiceAgent
app = FastAPI()
origins = [
    "https://rag-agent-iota.vercel.app", 
     "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
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

async def generate_response(chatbot: ChatBot, chat_id: str, message: str):
    print(f"[{chat_id}] Processing message for chat_id: {chat_id}")
    buffer=['"','-','*','—']
    flush=False
    async for token in chatbot.ask_stream(message, session_id=chat_id, k=3):
        if token in buffer:
            if flush:
                flush=False
                continue
            else:
                flush=True
        yield token

def file_processing(files: List[UploadFile],chatbot: ChatBot,chat_id:str):
    for file in files:
        if file.filename:
            print(f"[{chat_id}] Processing file: {file.filename}")
            try:
                print(file.file)
                chatbot.read(file.file,filename= file.filename)
            except Exception as file_error:
                print(f"[{chat_id}] Error reading file {file.filename}: {file_error}")

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
            file_processing(files,chatbot,chat_id)

        
        return StreamingResponse(
            generate_response(chatbot, chat_id, message),
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
    

@app.websocket("/voice")
async def voice_endpoint(websocket:WebSocket,chat_id: str=Query(...)):
    await websocket.accept()
    buffer=io.BytesIO()
    try:
        while True:
            chunk=await websocket.receive()
            if 'bytes' in chunk:
                buffer.write(chunk['bytes'])
            if 'text' in chunk:
                break
          
        audio_bytes=buffer.getvalue()
        chat_bot=get_or_create_chatbot(chat_id)
        agent=VoiceAgent()
        transcription=agent.transcribe_bytes(audio_bytes)
        async for token in generate_response(chatbot=chat_bot,chat_id=chat_id,message=transcription):
            await websocket.send_text(token)


    except WebSocketDisconnect:
        print("WebSocket disconnected")

    return {"message": "Voice endpoint is under construction."}