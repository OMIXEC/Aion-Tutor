import os
import uvicorn
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from aion_tutor.tools import (
    search_web_deep,
)

load_dotenv()

search_agent = LlmAgent(
    name="deep_search",
    model="gemini-2.5-flash",
    description=(
        "Searches the web for real-time information using Perplexity Sonar. "
        "Use for current events, latest frameworks, documentation, or any query "
        "requiring up-to-date internet knowledge beyond the training cutoff."
    ),
    instruction=(
        "You are the Deep Web Search Agent. "
        "Use search_web_deep to query Perplexity Sonar API for fresh, accurate information. "
        "Summarize results clearly and cite key sources when available."
    ),
    tools=[
        search_web_deep,
    ],
)

if __name__ == "__main__":
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from agents.server import create_agent_app

    session_service = InMemorySessionService()
    runner = Runner(app_name="aion-tutor", agent=search_agent, session_service=session_service)
    app = create_agent_app("deep_search", "Deep Search Agent", runner)

    port = int(os.getenv("SEARCH_PORT", 8007))
    uvicorn.run(app, host="0.0.0.0", port=port)
