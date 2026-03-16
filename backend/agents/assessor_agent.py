import os
import uvicorn
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.agents.llm_agent import LlmAgent

PORT = int(os.environ.get("PORT", 8003))
HOST = os.environ.get("AGENT_HOST", "0.0.0.0")

def main() -> None:
    root_agent = LlmAgent(
        model="gemini-3-pro",
        name="SilentAssessor",
        instruction=(
            "You are a silent, highly accurate Assessor. You invisibly evaluate the user's responses. "
            "Determine if the user correctly understood the concept based on their active recall and Feynman explanations. "
            "Output ONLY a valid JSON payload matching the schema: {\"concept_mastered\": bool, \"topic\": \"Topic Name\", \"confidence\": float (0-1), \"reasoning\": \"Short reason\"}. "
            "Do not include markdown or external text. Do not speak to the user directly."
        )
    )
    
    a2a_app = to_a2a(root_agent, host=HOST, port=PORT)
    print("Running Silent Assessor Agent")
    uvicorn.run(a2a_app, host=HOST, port=PORT)

if __name__ == "__main__":
    main()
