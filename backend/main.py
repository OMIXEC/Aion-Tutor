import asyncio
import json
import logging
import warnings
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from google.adk.agents.live_request_queue import LiveRequestQueue
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Load environment variables
load_dotenv()

# Import the root orchestrator agent from the agents package
from agents import root_agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Suppress Pydantic serialization warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

APP_NAME = "aion-tutor"

# ========================================
# Phase 1: Application Initialization
# ========================================

app = FastAPI(title="Aion Tutor Orchestrator", version="2.5.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Shared services
session_service = InMemorySessionService()
runner = Runner(app_name=APP_NAME, agent=root_agent, session_service=session_service)

@app.get("/")
async def root():
    return {"status": "Aion Tutor Bidi-Streaming Orchestrator is operational.", "model": root_agent.model}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "agent": root_agent.name,
        "sub_agents": [
            "socratic_tutor",
            "curriculum_planner",
            "silent_assessor",
            "rag_knowledge",
            "profile_manager",
            "deep_search",
        ]
    }

# ========================================
# WebSocket Endpoint (Multimodal Bidi)
# ========================================

@app.websocket("/ws/session/{user_id}/{session_id}")
async def websocket_session(
    websocket: WebSocket,
    user_id: str,
    session_id: str,
    proactivity: bool = False,
    affective_dialog: bool = False,
):
    """
    Multimodal WebSocket supporting Text, Audio, and Video.
    Follows the ADK Bidi-streaming pattern for Gemini Live.
    """
    logger.info(f"WebSocket connecting: user={user_id}, session={session_id}")
    await websocket.accept()

    # Determine modalities based on model
    model_name = root_agent.model
    # The user specifically requested gemini-live-2.5-flash-native-audio
    is_native_audio = "native-audio" in model_name.lower()

    if is_native_audio:
        response_modalities = ["AUDIO"]
        run_config = RunConfig(
            streaming_mode=StreamingMode.BIDI,
            response_modalities=response_modalities,
            input_audio_transcription=types.AudioTranscriptionConfig(),
            output_audio_transcription=types.AudioTranscriptionConfig(),
            session_resumption=types.SessionResumptionConfig(),
            proactivity=(
                types.ProactivityConfig(proactive_audio=True) if proactivity else None
            ),
            enable_affective_dialog=affective_dialog if affective_dialog else None,
        )
    else:
        response_modalities = ["TEXT"]
        run_config = RunConfig(
            streaming_mode=StreamingMode.BIDI,
            response_modalities=response_modalities,
            session_resumption=types.SessionResumptionConfig(),
        )

    # Ensure session exists
    session = await session_service.get_session(app_name=APP_NAME, user_id=user_id, session_id=session_id)
    if not session:
        await session_service.create_session(app_name=APP_NAME, user_id=user_id, session_id=session_id)

    live_request_queue = LiveRequestQueue()

    async def upstream_task():
        """Handle incoming WebSocket data (Text, Audio, Video)."""
        try:
            while True:
                message = await websocket.receive()

                # 1. Binary Audio Data
                if "bytes" in message:
                    audio_data = message["bytes"]
                    audio_blob = types.Blob(mime_type="audio/pcm;rate=16000", data=audio_data)
                    live_request_queue.send_realtime(audio_blob)

                # 2. Text or JSON (Images/Text)
                elif "text" in message:
                    text_data = message["text"]
                    json_msg = json.loads(text_data)

                    if json_msg.get("type") == "text" or "message" in json_msg:
                        text_content = json_msg.get("text") or json_msg.get("message")
                        content = types.Content(parts=[types.Part(text=text_content)])
                        live_request_queue.send_content(content)

                    elif json_msg.get("type") == "image":
                        import base64
                        image_data = base64.b64decode(json_msg["data"])
                        mime_type = json_msg.get("mimeType", "image/jpeg")
                        image_blob = types.Blob(mime_type=mime_type, data=image_data)
                        live_request_queue.send_realtime(image_blob)
        except Exception as e:
            logger.error(f"Upstream error: {e}")

    async def downstream_task():
        """Handle outgoing events from Runner to WebSocket."""
        try:
            async for event in runner.run_live(
                user_id=user_id,
                session_id=session_id,
                live_request_queue=live_request_queue,
                run_config=run_config,
            ):
                event_json = event.model_dump_json(exclude_none=True, by_alias=True)
                await websocket.send_text(event_json)
        except Exception as e:
            logger.error(f"Downstream error: {e}")

    try:
        await asyncio.gather(upstream_task(), downstream_task())
    except WebSocketDisconnect:
        logger.info("Client disconnected")
    finally:
        live_request_queue.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
