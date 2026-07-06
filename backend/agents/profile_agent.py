import os
import uvicorn
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from aion_tutor.tools import (
    fetch_user_profile,
    update_profile,
    update_topic_mastery,
    create_session,
)

load_dotenv()

profile_agent = LlmAgent(
    name="profile_manager",
    model="gemini-2.5-flash",
    description=(
        "Manages learner profiles in Supabase. Use for profile lookups, "
        "goal updates, onboarding data storage, or mastery tracking requests."
    ),
    instruction=(
        "You are the Profile & Memory Manager. "
        "Use fetch_user_profile to read the learner's state from Supabase. "
        "Use update_profile to update top-level fields (mission, goal, onboarding). "
        "Use update_topic_mastery to update mastery scores reported by the Assessor. "
        "Always work with exact Supabase user UUIDs."
    ),
    tools=[
        fetch_user_profile,
        update_profile,
        update_topic_mastery,
        create_session,
    ],
)

if __name__ == "__main__":
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from agents.server import create_agent_app

    session_service = InMemorySessionService()
    runner = Runner(app_name="aion-tutor", agent=profile_agent, session_service=session_service)
    app = create_agent_app("profile_manager", "Profile Manager Agent", runner)

    port = int(os.getenv("PROFILE_PORT", 8005))
    uvicorn.run(app, host="0.0.0.0", port=port)
