import os
import uvicorn
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from aion_tutor.tools import (
    fetch_user_profile,
    search_knowledge_base,
    search_web_deep,
)

load_dotenv()

planner_agent = LlmAgent(
    name="curriculum_planner",
    model="gemini-2.5-flash",
    description=(
        "Generates personalized learning curricula. Use for study planning, "
        "goal setting, roadmap creation, or scheduling requests."
    ),
    instruction=(
        "You are an expert Curriculum Planner. "
        "Always call fetch_user_profile first to understand the learner's experience, background, current tasks, constraints/requirements, and context. "
        "If the user has enabled deep search use search_web_deep to ensure the plan includes the latest tools and frameworks. "
        "Use search_knowledge_base to understand available curriculum content. "
        "Output a structured JSON list of personalized learning milestones:\n"
        '["Topic 1", "Topic 2", "Topic 3"]\n'
        "Keep it under 5 focused milestones. Heavily personalize based on the user's existing knowledge, "
        "certifications, tasks, tags, requirements, and goal/mission."
    ),
    tools=[
        fetch_user_profile,
        search_knowledge_base,
        search_web_deep,
    ],
)

if __name__ == "__main__":
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from agents.server import create_agent_app

    session_service = InMemorySessionService()
    runner = Runner(app_name="aion-tutor", agent=planner_agent, session_service=session_service)
    app = create_agent_app("curriculum_planner", "Curriculum Planner Agent", runner)

    port = int(os.getenv("PLANNER_PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port)
