import os
import uvicorn
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from aion_tutor.tools import (
    search_knowledge_base,
    search_semantic_memories,
    save_message,
)

load_dotenv()

tutor_agent = LlmAgent(
    name="socratic_tutor",
    model="gemini-2.5-flash",
    description=(
        "Expert Socratic tutor that explains concepts using analogies, "
        "guiding questions, and the Feynman technique. Use for all tutoring, "
        "concept explanation, and deep learning requests."
    ),
    instruction=(
        "You are an elite Socratic AI Tutor. You NEVER give direct answers. "
        "Use search_knowledge_base to retrieve curriculum context first. "
        "Use search_semantic_memories to recall what the user already knows or struggled with. "
        "Save key exchanges with save_message using role='assistant'. "
        "Apply these methodologies:\n"
        "- Feynman Technique: Ask the user to explain concepts simply.\n"
        "- Spaced Repetition: Quiz on prior knowledge instead of passively giving info.\n"
        "- Analogical Reasoning: Map new concepts to the user's existing knowledge (e.g., their AWS or ML background).\n"
        "- Mind Mapping: Help connect new concepts to their knowledge graph.\n"
        "Always adapt technical depth to the learner's experience level."
    ),
    tools=[
        search_knowledge_base,
        search_semantic_memories,
        save_message,
    ],
)

if __name__ == "__main__":
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from agents.server import create_agent_app

    session_service = InMemorySessionService()
    runner = Runner(app_name="aion-tutor", agent=tutor_agent, session_service=session_service)
    app = create_agent_app("socratic_tutor", "Socratic Tutor Agent", runner)

    port = int(os.getenv("TUTOR_PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
