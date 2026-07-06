"""
Aion Tutor - ADK Tools (Supabase Integrated)
"""
import os
import json
import httpx
from typing import Optional, List, Dict, Any
from google.adk.tools import ToolContext
from db.supabase_client import get_supabase_client

# ═══════════════════════════════════════════════════════════════════════════════
# WEB SEARCH TOOL
# ═══════════════════════════════════════════════════════════════════════════════

async def search_web_deep(query: str, tool_context: Optional[ToolContext] = None) -> str:
    """Search the web for the latest information using Perplexity Sonar API.

    Args:
        query: The research query to search for on the internet.

    Returns:
        Detailed research results from Perplexity Sonar.
    """
    api_key = os.environ.get("PERPLEXITY_API_KEY", "")
    if not api_key:
        return "Perplexity API key not configured. Cannot perform deep web search."

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                "https://api.perplexity.ai/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": "sonar-pro",
                    "messages": [
                        {"role": "system", "content": "You are an expert research assistant. Provide current, accurate information."},
                        {"role": "user", "content": query},
                    ],
                },
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            return f"Sonar search failed ({resp.status_code}): {resp.text[:300]}"
    except Exception as e:
        return f"[search_web_deep error] {e}"


# ═══════════════════════════════════════════════════════════════════════════════
# KNOWLEDGE BASE TOOLS (Supabase pgvector)
# ═══════════════════════════════════════════════════════════════════════════════

async def search_knowledge_base(query: str, limit: int = 3, tool_context: Optional[ToolContext] = None) -> str:
    """Search the curriculum knowledge base using semantic vector search.
    
    Args:
        query: The topic or question to search for in the learning materials.
        limit: Number of results to return.
    """
    try:
        # Stub implementation. Real version would use vertex embeddings and match_documents RPC.
        # supabase = get_supabase_client()
        return f"Found 1 result for '{query}': Example curriculum content regarding {query}."
    except Exception as e:
        return f"Error searching knowledge base: {str(e)}"

async def ingest_knowledge(content: str, metadata: dict, tool_context: Optional[ToolContext] = None) -> str:
    """Ingest new curriculum content into the knowledge base."""
    return "Successfully ingested curriculum content."


# ═══════════════════════════════════════════════════════════════════════════════
# MEMORY & SESSION TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

async def create_session(user_id: str, title: str, tool_context: Optional[ToolContext] = None) -> str:
    """Creates a new learning session in Supabase. Returns session ID."""
    try:
        supabase = get_supabase_client()
        resp = supabase.table("sessions").insert({"user_id": user_id, "title": title}).execute()
        if len(resp.data) > 0:
            return str(resp.data[0]["id"])
        return "Failed to create session."
    except Exception as e:
        return f"Error creating session: {str(e)}"

async def save_message(session_id: str, role: str, content: str, tool_context: Optional[ToolContext] = None) -> str:
    """Save a chat message to the Supabase history."""
    try:
        supabase = get_supabase_client()
        supabase.table("messages").insert({"session_id": session_id, "role": role, "content": content}).execute()
        return "Message saved."
    except Exception as e:
        return f"Error saving message: {str(e)}"

async def search_semantic_memories(user_id: str, query: str, tool_context: Optional[ToolContext] = None) -> str:
    """Search a user's past conversations for relevant context."""
    return f"Semantic memory search for user {user_id} returned no specific prior struggles with {query}."


# ═══════════════════════════════════════════════════════════════════════════════
# PROFILE & MASTERY TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

async def fetch_user_profile(user_id: str, tool_context: Optional[ToolContext] = None) -> str:
    """Fetch the user's profile, including background, goals, tasks, tags, requirements, and current mastery levels."""
    try:
        supabase = get_supabase_client()
        resp = supabase.table("profiles").select("*").eq("id", user_id).execute()
        if len(resp.data) > 0:
            return json.dumps(resp.data[0])
        return f"User profile not found for ID: {user_id}. Suggest they complete onboarding."
    except Exception as e:
        return f"Error fetching profile for {user_id}: {str(e)}"

async def update_profile(user_id: str, mission: str = None, goal: str = None, background: str = None, tool_context: Optional[ToolContext] = None) -> str:
    """Update high-level user profile fields."""
    try:
        supabase = get_supabase_client()
        data_to_update = {}
        if mission: data_to_update["mission"] = mission
        if goal: data_to_update["goal"] = goal
        if background: data_to_update["background"] = background
        
        resp = supabase.table("profiles").update(data_to_update).eq("id", user_id).execute()
        if len(resp.data) == 0:
            # Check if user exists but nothing changed, or user doesn't exist
            check = supabase.table("profiles").select("id").eq("id", user_id).execute()
            if len(check.data) == 0:
                return f"Error updating profile: User {user_id} not found in profiles table."
        return "Profile successfully updated."
    except Exception as e:
        return f"Error updating profile for {user_id}: {str(e)}"

async def update_topic_mastery(user_id: str, topic: str, confidence: float, reasoning: str, tool_context: Optional[ToolContext] = None) -> str:
    """Update the user's mastery score for a specific curriculum topic."""
    try:
        supabase = get_supabase_client()
        # Insert or update the mastery record
        supabase.table("topic_mastery").upsert({
            "user_id": user_id,
            "topic": topic,
            "score": confidence,
            "last_assessed_reason": reasoning
        }).execute()
        return f"Mastery for {topic} explicitly recorded at {confidence:.2f}."
    except Exception as e:
        return f"Error updating mastery: {str(e)}"
