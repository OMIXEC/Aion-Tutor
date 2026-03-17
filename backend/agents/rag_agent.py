import os
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.agents.llm_agent import LlmAgent

PORT = int(os.environ.get("PORT", 8003)) # Fixed port mapping
HOST = os.environ.get("AGENT_HOST", "0.0.0.0")

def search_knowledge_base(query: str) -> str:
    """Mock query for knowledge base to demonstrate agent functionality without Supabase."""
    return f"Information about '{query}': Based on standard educational curriculum, you should focus on the core principles and interactive practice."

root_agent = LlmAgent(
    model="gemini-2.0-flash-exp",
    name="RagAgent",
    tools=[search_knowledge_base],
    instruction=(
        "You are the Information Retrieval Agent. Query the Supabase vector database "
        "using the `search_knowledge_base` tool with semantic similarity search to find the most relevant educational content. "
        "Provide factual, concise extracts to the Tutor agent."
    )
)

app = to_a2a(root_agent, host=HOST, port=PORT)

if __name__ == "__main__":
    import uvicorn
    print("Running RAG Agent")
    uvicorn.run(app, host=HOST, port=PORT)

