"""
Aion Tutor Backend — Integration Tests
Tests the new unified ADK backend (app.py).
"""
import pytest
import os
from fastapi.testclient import TestClient

# Provide mock env values before importing the app
os.environ.setdefault("GEMINI_API_KEY", "mock_key_for_testing")
os.environ.setdefault("SUPABASE_URL", "")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "")

from main import app

client = TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_200(self):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_agent_info(self):
        data = client.get("/health").json()
        assert data["status"] == "healthy"
        assert data["agent"] == "aion_orchestrator"
        assert isinstance(data["sub_agents"], list)
        assert len(data["sub_agents"]) == 6

    def test_health_lists_all_sub_agents(self):
        data = client.get("/health").json()
        expected = {
            "socratic_tutor",
            "curriculum_planner",
            "silent_assessor",
            "rag_knowledge",
            "profile_manager",
            "deep_search",
        }
        assert expected == set(data["sub_agents"])


class TestAgentStructure:
    def test_root_agent_importable(self):
        from agents import root_agent
        assert root_agent.name == "aion_orchestrator"

    def test_root_agent_has_six_tools(self):
        from agents import root_agent
        # Since we use tools for A2A delegation now
        assert len(root_agent.tools) == 6


    def test_tools_importable(self):
        from aion_tutor.tools import (
            search_knowledge_base,
            search_semantic_memories,
            fetch_user_profile,
            update_topic_mastery,
            save_message,
            search_web_deep,
        )
        # All tools are callable
        for tool in [search_knowledge_base, search_semantic_memories,
                     fetch_user_profile, update_topic_mastery, save_message, search_web_deep]:
            assert callable(tool)


class TestLegacyAgentsPreserved:
    """Verify legacy agent files still exist (not deleted)."""
    import pathlib
    AGENTS_DIR = pathlib.Path("backend/agents")

    def test_orchestrator_agent_exists(self):
        from pathlib import Path
        assert Path("agents/orchestrator_agent.py").exists() or \
               Path("backend/agents/orchestrator_agent.py").exists()

    def test_rag_agent_exists(self):
        from pathlib import Path
        assert Path("agents/rag_agent.py").exists() or \
               Path("backend/agents/rag_agent.py").exists()
