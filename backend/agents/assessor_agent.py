import os
import uvicorn
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from aion_tutor.tools import (
    update_topic_mastery,
    save_message,
)

load_dotenv()

assessor_agent = LlmAgent(
    name="silent_assessor",
    model="gemini-2.5-flash",
    description=(
        "Invisibly evaluates learner comprehension and updates mastery scores. "
        "Use after any student response to quietly assess understanding."
    ),
    instruction=(
        "You are a silent, highly accurate Assessor. "
        "Evaluate the user's last response for comprehension depth. "
        "Call update_topic_mastery to record the result in Supabase profiles. "
        "Output ONLY valid JSON — no markdown, no prose:\n"
        '{"concept_mastered": bool, "topic": "Topic Name", "confidence": 0.0-1.0, "reasoning": "..."}\n'
        "Do NOT speak to the user directly. Be invisible."
    ),
    tools=[
        update_topic_mastery,
        save_message,
    ],
)

if __name__ == "__main__":
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from agents.server import create_agent_app

    session_service = InMemorySessionService()
    runner = Runner(app_name="aion-tutor", agent=assessor_agent, session_service=session_service)
    app = create_agent_app("silent_assessor", "Silent Assessor Agent", runner)

    port = int(os.getenv("ASSESSOR_PORT", 8004))
    uvicorn.run(app, host="0.0.0.0", port=port)
