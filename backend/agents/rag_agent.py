import os
import uvicorn
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from aion_tutor.tools import (
    search_knowledge_base,
)

load_dotenv()

rag_agent = LlmAgent(
    name="rag_knowledge",
    model="gemini-2.5-flash",
    description=(
        "Retrieves factual content from the Supabase pgvector knowledge base. "
        "Use for precise factual lookups, documentation search, or syllabus queries."
    ),
    instruction=(
        "You are the Information Retrieval Agent. "
        "Use search_knowledge_base to perform semantic vector search over the curriculum database. "
        "Return concise, accurate excerpts from matched documents. "
        "If nothing is found, say so clearly. Do not hallucinate."
    ),
    tools=[
        search_knowledge_base,
    ],
)

if __name__ == "__main__":
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from agents.server import create_agent_app

    session_service = InMemorySessionService()
    runner = Runner(app_name="aion-tutor", agent=rag_agent, session_service=session_service)
    app = create_agent_app("rag_knowledge", "RAG Knowledge Agent", runner)

    port = int(os.getenv("RAG_PORT", 8003))
    uvicorn.run(app, host="0.0.0.0", port=port)
