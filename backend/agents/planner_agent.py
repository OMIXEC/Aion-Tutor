import os
import requests
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools import google_search

PORT = int(os.environ.get("PORT", 8002))
HOST = os.environ.get("AGENT_HOST", "0.0.0.0")

def execute_sonar_search(query: str) -> str:
    """Calls Perplexity Sonar API for deep search concerning curriculum updates."""
    sonar_api_key = os.environ.get("PERPLEXITY_API_KEY", "")
    if not sonar_api_key:
        return "Perplexity API Key missing. Cannot perform deep search."
        
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {sonar_api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": "You are an expert educational researcher finding the latest, most up-to-date technologies and best practices for this specific topic."},
            {"role": "user", "content": query}
        ]
    }
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60.0)
        if resp.status_code == 200:
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        else:
            return f"Sonar search failed: {resp.text}"
    except Exception as e:
        return f"Sonar Exception: {e}"


root_agent = LlmAgent(
    model="gemini-3-pro",
    name="CurriculumPlanner",
    tools=[google_search, execute_sonar_search],
    instruction=(
        "You are an expert curriculum Planner, operating as an advanced prompt engineer. "
        "Analyze the student's learning target and intensely integrate their specific context "
        "(experience, tags, knowledge base, IT certifications) to structure a personalized curriculum sequence. "
        "Use the `google_search` or `execute_sonar_search` tools to ensure the syllabus strictly includes the latest libraries, methods, or updates required. "
        "Output ONLY a JSON list of strings (e.g., [\"Authentication with JWT\", \"Postgres Scaling\"]). "
        "Keep it under 3 extremely tailored items for this demo."
    )
)

app = to_a2a(root_agent, host=HOST, port=PORT)

if __name__ == "__main__":
    import uvicorn
    print("Running Curriculum Planner Agent")
    uvicorn.run(app, host=HOST, port=PORT)
