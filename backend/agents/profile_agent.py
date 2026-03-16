import os
import json
import uvicorn
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.agents.llm_agent import LlmAgent

PORT = int(os.environ.get("PORT", 8005))
HOST = os.environ.get("AGENT_HOST", "0.0.0.0")

_mock_profiles = {}

def manage_profile(user_id: str, action: str, data: str = "") -> str:
    """Fetch or update the user's profile and background context."""
    if user_id not in _mock_profiles:
        _mock_profiles[user_id] = {
            "learning_goal": "Learn modern Web Development",
            "background_context": {
                "experience_level": "Beginner",
                "primary_topics": "HTML, CSS, JavaScript",
                "certifications": "None",
                "tags": "frontend, web",
                "knowledge": "Basic programming concepts"
            },
            "topic_mastery": {}
        }
        
    profile = _mock_profiles[user_id]
    
    if action == "update" and data:
        try:
            mastery_update = json.loads(data)
            profile["topic_mastery"].update(mastery_update)
            return f"Mastery updated successfully: {json.dumps(profile['topic_mastery'])}"
        except Exception as e:
            return f"Failed to update profile: {e}"

    # Default: fetch
    bg = profile.get("background_context", {})
    context_summary = (
        f"Goal: {profile.get('learning_goal', 'N/A')}. "
        f"Experience: {bg.get('experience_level', 'N/A')}. "
        f"Topics: {bg.get('primary_topics', 'N/A')}. "
        f"Certs: {bg.get('certifications', 'N/A')}. "
        f"Tags: {bg.get('tags', 'N/A')}. "
        f"Base Knowledge: {bg.get('knowledge', 'N/A')}."
    )
    return context_summary

def main() -> None:
    root_agent = LlmAgent(
        model="gemini-3-pro",
        name="ProfileManager",
        tools=[manage_profile],
        instruction=(
            "You are the Profile & Memory Manager. You will receive a JSON string containing the 'action', "
            "and optionally 'data' and 'user_id' (if provided in the prompt). "
            "Extract the 'user_id' from the prompt. If none is provided, use 'guest'. "
            "Use the `manage_profile` tool to fetch or update the user's profile. "
            "Output the resulting context summary or update confirmation directly."
        )
    )
    
    a2a_app = to_a2a(root_agent, host=HOST, port=PORT)
    print("Running Profile Agent")
    uvicorn.run(a2a_app, host=HOST, port=PORT)

if __name__ == "__main__":
    main()
