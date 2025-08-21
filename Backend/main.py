from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio


from fastapi.middleware.cors import CORSMiddleware
from ChatBot import ChatBot


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or list your frontend domains
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active connections: id -> websocket
connections = {}

@app.websocket("/ws/{id}")
async def websocket_endpoint(websocket: WebSocket, id: str):
    """
    One WebSocket connection per unique id.
    Each id runs independently.
    """
    await websocket.accept()
    connections[id] = websocket
    print(f"[{id}] WebSocket connected")

    chatbot = ChatBot()  # Initialize your chatbot instance


    try:
        while True:
            # Receive messages from frontend
            data = await websocket.receive_text()
            print(f"[{id}] Received: {data}")
            for file in data.get("files", []):
                chatbot.read(file,file.name)  # Read files using the chatbot's read method

            # You can access `id` anywhere in this loop
            # Example: print or use it for routing logic
            print(f"Processing message for connection id: {id}")

            # Simulate independent processing per id
            # (keep your existing logic here)

    except WebSocketDisconnect:
        print(f"[{id}] WebSocket disconnected")
        connections.pop(id, None)
