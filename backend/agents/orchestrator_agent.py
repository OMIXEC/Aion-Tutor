"""
Aion Tutor — Multimodal A2A Orchestrator
root_agent = Orchestrator with remote sub-agents via A2A
Each sub-agent runs independently on its own port.
"""
import os
import httpx
import json
import asyncio
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.genai import types as genai_types

load_dotenv()

# Port mapping from test_a2a.py
AGENT_PORTS = {
    "socratic_tutor": os.getenv("TUTOR_PORT", 8001),
    "curriculum_planner": os.getenv("PLANNER_PORT", 8002),
    "rag_knowledge": os.getenv("RAG_PORT", 8003),
    "silent_assessor": os.getenv("ASSESSOR_PORT", 8004),
    "profile_manager": os.getenv("PROFILE_PORT", 8005),
    "deep_search": os.getenv("SEARCH_PORT", 8007),
}

async def _call_remote_agent(agent_name: str, content: str, user_id: str, session_id: str) -> str:
    """Helper to call an independent A2A agent service."""
    port = AGENT_PORTS.get(agent_name)
    if not port:
        return f"Error: Agent {agent_name} not found in port mapping."

    url = f"http://localhost:{port}/execute"
    payload = {
        "content": content,
        "user_id": user_id,
        "session_id": session_id
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=30.0)
            if response.status_code == 200:
                return response.json().get("reply", "No response from agent.")
            else:
                return f"Error calling {agent_name}: Status {response.status_code}"
        except Exception as e:
            return f"Network error calling {agent_name}: {str(e)}"

# ─────────────────────────────────────────────────────────────
# DELEGATION TOOLS (A2A)
# ─────────────────────────────────────────────────────────────

async def delegate_to_tutor(query: str, user_id: str, session_id: str) -> str:
    """Delegate to the Socratic Tutor for concept explanation and deep learning."""
    return await _call_remote_agent("socratic_tutor", query, user_id, session_id)

async def delegate_to_planner(query: str, user_id: str, session_id: str) -> str:
    """Delegate to the Curriculum Planner for study roadmaps and goal setting."""
    return await _call_remote_agent("curriculum_planner", query, user_id, session_id)

async def delegate_to_rag(query: str, user_id: str, session_id: str) -> str:
    """Delegate to RAG Knowledge for factual curriculum data lookup."""
    return await _call_remote_agent("rag_knowledge", query, user_id, session_id)

async def delegate_to_assessor(query: str, user_id: str, session_id: str) -> str:
    """Delegate to the Silent Assessor to evaluate learner comprehension quietly."""
    return await _call_remote_agent("silent_assessor", query, user_id, session_id)

async def delegate_to_profile(query: str, user_id: str, session_id: str) -> str:
    """Delegate to the Profile Manager for profile edits, mastery scores, and user context."""
    return await _call_remote_agent("profile_manager", query, user_id, session_id)

async def delegate_to_search(query: str, user_id: str, session_id: str) -> str:
    """Delegate to Deep Search for real-time web information and latest tech."""
    return await _call_remote_agent("deep_search", query, user_id, session_id)

# ─────────────────────────────────────────────────────────────
# ROOT AGENT — Gemini Live Orchestrator
# ─────────────────────────────────────────────────────────────
root_agent = LlmAgent(
    name="aion_orchestrator",
    model="gemini-2.5-flash-native-audio-latest",
    description="Aion Tutor — Adaptive AI learning orchestrator using native audio and A2A delegation.",
    instruction=(
        "You are the master Orchestrator of the Aion Tutor system. "
        "You have direct access to a fleet of specialized A2A agents via your tools. "
        "Maintain a fluid, natural conversation with the learner using your native audio capabilities. "

        "Delegation Strategy:\n"
        "• delegate_to_tutor    → Use for deep concept explanations, Socratic tutoring.\n"
        "• delegate_to_planner  → Use to create or modify study plans and roadmaps.\n"
        "• delegate_to_assessor → Use silently after student replies to track their progress.\n"
        "• delegate_to_rag      → Use for factual curriculum/textbook lookups.\n"
        "• delegate_to_profile  → Use to fetch or update learner background, tasks, and requirements.\n"
        "• delegate_to_search   → Use for real-time internet research.\n\n"

        "Guidelines:\n"
        "1. After EVERY student response, call delegate_to_assessor to keep mastery scores updated.\n"
        "2. At session start, call delegate_to_profile to fetch the learner's context (tasks, requirements, background).\n"
        "3. Keep your direct spoken responses concise and motivational.\n"
        "4. Always unify the intelligence of your sub-agents to provide a personalized experience.\n"
        "5. NEVER mention that you are calling 'tools' or 'sub-agents'. Mask the technology behind a seamless tutoring persona."
    ),
    tools=[
        delegate_to_tutor,
        delegate_to_planner,
        delegate_to_assessor,
        delegate_to_rag,
        delegate_to_profile,
        delegate_to_search,
    ],
    generate_content_config=genai_types.GenerateContentConfig(
        temperature=0.7,
        max_output_tokens=2048,
        response_modalities=["AUDIO"], # Default for native audio model
    ),
)
