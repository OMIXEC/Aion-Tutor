"""
Aion Tutor - ADK Tools (Supabase removed)
"""
import os
import json
import httpx
from typing import Optional
from google.adk.tools import ToolContext

# ═══════════════════════════════════════════════════════════════════════════════
# WEB SEARCH TOOL — Perplexity Sonar API
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
