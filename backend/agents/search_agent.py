import os
import requests
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools import google_search

PORT = int(os.environ.get("PORT", 8007))
HOST = os.environ.get("AGENT_HOST", "0.0.0.0")

def execute_sonar_search(query: str) -> str:
    """Calls Perplexity Sonar API for deep, complex research queries."""
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
            {"role": "system", "content": "You are a research assistant compiling fresh, highly technical data on this topic."},
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
    name="SearchEngine",
    tools=[google_search, execute_sonar_search],
    instruction=(
        "You are the Search Agent, equipped to find information online. "
        "Analyze the user's query. If it requires deep research, complex synthesis, or highly specific IT technical details, "
        "use the `execute_sonar_search` tool. If it is a basic factual question or simple lookup, use the `google_search` tool. "
        "Return the detailed search results concisely. State which source/tool you used at the end of the response."
    )
)

app = to_a2a(root_agent, host=HOST, port=PORT)

if __name__ == "__main__":
    import uvicorn
    print("Running Deep Web Search Agent")
    uvicorn.run(app, host=HOST, port=PORT)
