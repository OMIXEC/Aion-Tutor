import os
import json
import asyncio
from typing import Optional, Dict, Any

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from google.adk.agents import LlmAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.agents.live_request_queue import LiveRequestQueue
from google.genai import types as genai_types

app = FastAPI(title="Aion Tutor Orchestrator", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────
# 1. SETUP REMOTE A2A AGENTS
# ─────────────────────────────────────────────────────────────
host = os.environ.get("AGENT_HOST", "0.0.0.0")

def create_remote_agent(name: str, port: int) -> RemoteA2aAgent:
    return RemoteA2aAgent(
        name=name,
        agent_card=f"http://{host}:{port}",
    )

tutor_agent = create_remote_agent("socratic_tutor", 8001)
planner_agent = create_remote_agent("curriculum_planner", 8002)
assessor_agent = create_remote_agent("silent_assessor", 8004)
rag_agent = create_remote_agent("rag_knowledge", 8003)
profile_agent = create_remote_agent("profile_manager", 8005)
search_agent = create_remote_agent("deep_search", 8007)

# ─────────────────────────────────────────────────────────────
# 2. DEFINE MASTER ORCHESTRATOR
# ─────────────────────────────────────────────────────────────
root_agent = LlmAgent(
    name="aion_orchestrator",
    model="gemini-2.0-flash-exp", # Using latest multimodal live compatible if available, or 1.5/2.0
    description="Aion Tutor Master Orchestrator",
    instruction=(
        "You are the master orchestrator of the Aion Tutor system.\n"
        "Your job is to maintain a fluid, engaging conversation with the user using voice/audio.\n"
        "You must delegate specific tasks to specialized sub-agents via tool calls:\n"
        "- socratic_tutor    → explaining concepts, teaching methodologies\n"
        "- curriculum_planner → study plans, roadmaps\n"
        "- silent_assessor   → quietly evaluate understanding (call in background)\n"
        "- rag_knowledge     → factual lookups from internal knowledge base\n"
        "- profile_manager   → fetch/update user learner profile\n"
        "- deep_search       → web search for real-time info\n\n"
        "Keep your direct answers brief and conversational. Wrap agent responses naturally "
        "into your spoken replies. Do NOT reveal your internal structure."
    ),
    sub_agents=[
        tutor_agent,
        planner_agent,
        assessor_agent,
        rag_agent,
        profile_agent,
        search_agent,
    ],
)

# ─────────────────────────────────────────────────────────────
# 3. RUNNER SETUP
# ─────────────────────────────────────────────────────────────
_session_service = InMemorySessionService()
_adk_runner = Runner(app_name="aion_tutor", agent=root_agent, session_service=_session_service)

@app.websocket("/ws/live/{session_id}")
async def websocket_live_session(websocket: WebSocket, session_id: str):
    await websocket.accept()
    query_params = websocket.query_params
    user_id = query_params.get("user_id", "guest")
    
    print(f"[bidi] Connected: user={user_id}, session={session_id}")

    run_config = RunConfig(
        streaming_mode=StreamingMode.BIDI,
        response_modalities=["AUDIO", "TEXT"],
        input_audio_transcription=genai_types.AudioTranscriptionConfig(),
        output_audio_transcription=genai_types.AudioTranscriptionConfig(),
    )

    # Ensure session exists
    session = await _session_service.get_session(app_name="aion_tutor", user_id=user_id, session_id=session_id)
    if not session:
        await _session_service.create_session(app_name="aion_tutor", user_id=user_id, session_id=session_id)

    live_request_queue = LiveRequestQueue()

    async def upstream():
        try:
            while True:
                data = await websocket.receive_text()
                payload = json.loads(data)
                
                if payload.get("realtime_input"):
                    chunk = payload["realtime_input"]["media_chunks"][0]
                    audio_blob = genai_types.Blob(
                        mime_type=chunk.get("mime_type", "audio/pcm;rate=16000"),
                        data=chunk["data"]
                    )
                    live_request_queue.send_realtime(audio_blob)
                
                elif payload.get("message"):
                    text = payload["message"]
                    profile = payload.get("profile", {})
                    if profile:
                        text = f"[Learner Context: {json.dumps(profile)}]\nUser: {text}"
                    content = genai_types.Content(parts=[genai_types.Part(text=text)])
                    live_request_queue.send_content(content)
        except WebSocketDisconnect:
            pass
        except Exception as e:
            print(f"[bidi] Upstream error: {e}")

    async def downstream():
        try:
            async for event in _adk_runner.run_live(
                user_id=user_id,
                session_id=session_id,
                live_request_queue=live_request_queue,
                run_config=run_config,
            ):
                # Send the ADK event to frontend
                await websocket.send_text(event.model_dump_json(exclude_none=True, by_alias=True))
        except Exception as e:
            print(f"[bidi] Downstream error: {e}")

    try:
        await asyncio.gather(upstream(), downstream())
    finally:
        live_request_queue.close()

@app.get("/health")
def health():
    return {"status": "healthy", "agent": root_agent.name}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

