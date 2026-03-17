import os
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.agents.llm_agent import LlmAgent

PORT = int(os.environ.get("PORT", 8001))
HOST = os.environ.get("AGENT_HOST", "0.0.0.0")

root_agent = LlmAgent(
    model="gemini-2.0-flash-exp",
    name="SocraticTutor",
    instruction=(
        "You are an elite Socratic AI Tutor. You NEVER give direct answers. "
        "Use the provided context (RAG) and the user's profile "
        "to draw analogies and ask guiding questions to help the user arrive at the answer themselves.\n"
        "You must employ the following teaching methodologies:\n"
        "- Feynman Technique: Ask the user to explain concepts simply.\n"
        "- Spaced Repetition & Active Recall: Quiz the user on prior knowledge rather than passively giving info.\n"
        "- Mind Mapping: Help the user connect new concepts to their existing knowledge graph."
    )
)

app = to_a2a(root_agent, host=HOST, port=PORT)

if __name__ == "__main__":
    import uvicorn
    print("Running Socratic Tutor Agent")
    uvicorn.run(app, host=HOST, port=PORT)
