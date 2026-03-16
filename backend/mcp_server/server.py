import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP("Aion-Agent-Registry")

# Define the absolute path to the agent_cards folder
BASE_DIR = Path(__file__).parent.resolve()
CARDS_DIR = BASE_DIR / "agent_cards"

def load_agent_card(filename: str) -> str:
    """Loads a JSON agent card from disk."""
    file_path = CARDS_DIR / filename
    if not file_path.exists():
        raise FileNotFoundError(f"Agent card not found: {filename}")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

@mcp.resource("agent://registry/tutor")
def get_tutor_card() -> str:
    """Returns the Socratic Tutor Agent Card"""
    return load_agent_card("tutor_agent.json")

@mcp.resource("agent://registry/planner")
def get_planner_card() -> str:
    """Returns the Curriculum Planner Agent Card"""
    return load_agent_card("planner_agent.json")

@mcp.resource("agent://registry/assessor")
def get_assessor_card() -> str:
    """Returns the Silent Assessor Agent Card"""
    return load_agent_card("assessor_agent.json")

@mcp.resource("agent://registry/rag")
def get_rag_card() -> str:
    """Returns the Pinecone RAG Agent Card"""
    return load_agent_card("rag_agent.json")

@mcp.resource("agent://registry/profile")
def get_profile_card() -> str:
    """Returns the Profile Manager Agent Card"""
    return load_agent_card("profile_agent.json")

@mcp.tool()
def find_agent(capability_keyword: str) -> str:
    """
    Finds and returns the JSON Agent Card of an agent that matches the capability keyword.
    Used by the Orchestrator to dynamically route A2A messages.
    """
    results = []
    if CARDS_DIR.exists():
        for file in CARDS_DIR.glob("*.json"):
            try:
                content = load_agent_card(file.name)
                card_data = json.loads(content)
                desc = card_data.get("description", "").lower()
                caps = str(card_data.get("capabilities", [])).lower()
                
                if capability_keyword.lower() in desc or capability_keyword.lower() in caps:
                    results.append(card_data)
            except Exception as e:
                print(f"Error reading {file.name}: {e}")
                
    return json.dumps(results, indent=2)

if __name__ == "__main__":
    # Start the MCP server using Standard I/O or SSE. 
    # For a microservice topology, SSE with FastAPI is preferred, 
    # but FastMCP handles stdio by default for simple usage.
    print(f"Starting Aion MCP Registry Server from {CARDS_DIR}...")
    mcp.run()
