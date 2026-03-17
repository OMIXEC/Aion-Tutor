import os
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from aion_tutor.agent import root_agent

load_dotenv()

app = FastAPI(title="Aion Tutor Backend", version="2.0.0")

# Enable CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "Aion Tutor Backend is running with ADK."}

@app.websocket("/ws/session/{session_id}")
async def websocket_session(websocket: WebSocket, session_id: str):
    await websocket.accept()
    print(f"[WebSocket] Client connected: Session {session_id}")
    try:
        while True:
            # 1. Wait for a message from the client
            data = await websocket.receive_text()
            payload = json.loads(data)
            user_message = payload.get("message", "")
            
            if not user_message:
                continue
                
            print(f"[WebSocket] Received from Session {session_id}: {user_message}")

            # 2. Add an indicator that the agent is thinking
            await websocket.send_text(json.dumps({"type": "status", "status": "typing"}))

            # 3. Stream the ADK swarm response
            # ADK provides stream() to get chunks back as they are generated.
            full_response = ""
            for chunk in root_agent.stream(user_message, session_id=session_id):
                full_response += chunk
                # Send the token to the frontend
                await websocket.send_text(json.dumps({
                    "type": "token",
                    "token": chunk
                }))

            # 4. Indicate that the agent has finished speaking
            await websocket.send_text(json.dumps({
                "type": "status",
                "status": "idle"
            }))
            
    except WebSocketDisconnect:
        print(f"[WebSocket] Client disconnected: Session {session_id}")
    except Exception as e:
        print(f"[WebSocket] Error: {e}")
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
