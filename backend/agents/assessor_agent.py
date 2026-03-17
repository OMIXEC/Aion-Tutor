import os
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.agents.llm_agent import LlmAgent

PORT = int(os.environ.get("PORT", 8004))
HOST = os.environ.get("AGENT_HOST", "0.0.0.0")

root_agent = LlmAgent(
    model="gemini-2.0-flash-exp",
    name="SilentAssessor",
    instruction=(
        "You are a silent, highly accurate Assessor. You invisibly evaluate the user's responses. "
        "Determine if the user correctly understood the concept based on their active recall and Feynman explanations. "
        "Output ONLY a valid JSON payload matching the schema: {\"concept_mastered\": bool, \"topic\": \"Topic Name\", \"confidence\": float (0-1), \"reasoning\": \"Short reason\"}. "
        "Do not include markdown or external text. Do not speak to the user directly."
    )
)

app = to_a2a(root_agent, host=HOST, port=PORT)

if __name__ == "__main__":
    import uvicorn
    print("Running Silent Assessor Agent")
    uvicorn.run(app, host=HOST, port=PORT)
