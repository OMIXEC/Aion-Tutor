"""
Aion Tutor — Native ADK Multi-Agent System
root_agent = Orchestrator with 6 sub-agents
All agents run in-process (no HTTP A2A). 
Supabase pgvector tools are injected as FunctionTools.

Compatible with:
  adk web aion_tutor          (local dev UI)
  adk deploy agent_engine     (Vertex AI Engine)
  uvicorn app:app             (custom FastAPI server)
"""
import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.genai import types as genai_types

load_dotenv()

from aion_tutor.tools import (
    # RAG
    search_knowledge_base,
    ingest_knowledge,
    # Memory
    search_semantic_memories,
    save_message,
    # Profile
    fetch_user_profile,
    update_topic_mastery,
    update_profile,
    # Sessions
    create_session,
    # Web
    search_web_deep,
)

# ─────────────────────────────────────────────────────────────
# 1. SOCRATIC TUTOR AGENT
# ─────────────────────────────────────────────────────────────
tutor_agent = LlmAgent(
    name="socratic_tutor",
    model="gemini-2.5-flash",
    description=(
        "Expert Socratic tutor that explains concepts using analogies, "
        "guiding questions, and the Feynman technique. Use for all tutoring, "
        "concept explanation, and deep learning requests."
    ),
    instruction=(
        "You are an elite Socratic AI Tutor. You NEVER give direct answers. "
        "Use search_knowledge_base to retrieve curriculum context first. "
        "Use search_semantic_memories to recall what the user already knows or struggled with. "
        "Save key exchanges with save_message using role='assistant'. "
        "Apply these methodologies:\n"
        "- Feynman Technique: Ask the user to explain concepts simply.\n"
        "- Spaced Repetition: Quiz on prior knowledge instead of passively giving info.\n"
        "- Analogical Reasoning: Map new concepts to the user's existing knowledge (e.g., their AWS or ML background).\n"
        "- Mind Mapping: Help connect new concepts to their knowledge graph.\n"
        "Always adapt technical depth to the learner's experience level."
    ),
    tools=[
        search_knowledge_base,
        search_semantic_memories,
        save_message,
    ],
)

# ─────────────────────────────────────────────────────────────
# 2. CURRICULUM PLANNER AGENT
# ─────────────────────────────────────────────────────────────
planner_agent = LlmAgent(
    name="curriculum_planner",
    model="gemini-2.5-flash",
    description=(
        "Generates personalized learning curricula. Use for study planning, "
        "goal setting, roadmap creation, or scheduling requests."
    ),
    instruction=(
        "You are an expert Curriculum Planner. "
        "Always call fetch_user_profile first to understand the learner's experience and context. "
        "If the user has enabled deep search use search_web_deep to ensure the plan includes the latest tools and frameworks. "
        "Use search_knowledge_base to understand available curriculum content. "
        "Output a structured JSON list of personalized learning milestones:\n"
        '["Topic 1", "Topic 2", "Topic 3"]\n'
        "Keep it under 5 focused milestones. Heavily personalize based on the user's existing knowledge, "
        "certifications, and goal/mission."
    ),
    tools=[
        fetch_user_profile,
        search_knowledge_base,
        search_web_deep,
    ],
)

# ─────────────────────────────────────────────────────────────
# 3. SILENT ASSESSOR AGENT
# ─────────────────────────────────────────────────────────────
assessor_agent = LlmAgent(
    name="silent_assessor",
    model="gemini-2.5-flash",
    description=(
        "Invisibly evaluates learner comprehension and updates mastery scores. "
        "Use after any student response to quietly assess understanding."
    ),
    instruction=(
        "You are a silent, highly accurate Assessor. "
        "Evaluate the user's last response for comprehension depth. "
        "Call update_topic_mastery to record the result in Supabase profiles. "
        "Output ONLY valid JSON — no markdown, no prose:\n"
        '{"concept_mastered": bool, "topic": "Topic Name", "confidence": 0.0-1.0, "reasoning": "..."}\n'
        "Do NOT speak to the user directly. Be invisible."
    ),
    tools=[
        update_topic_mastery,
        save_message,
    ],
)

# ─────────────────────────────────────────────────────────────
# 4. RAG KNOWLEDGE AGENT
# ─────────────────────────────────────────────────────────────
rag_agent = LlmAgent(
    name="rag_knowledge",
    model="gemini-2.5-flash",
    description=(
        "Retrieves factual content from the Supabase pgvector knowledge base. "
        "Use for precise factual lookups, documentation search, or syllabus queries."
    ),
    instruction=(
        "You are the Information Retrieval Agent. "
        "Use search_knowledge_base to perform semantic vector search over the curriculum database. "
        "Return concise, accurate excerpts from matched documents. "
        "If nothing is found, say so clearly. Do not hallucinate."
    ),
    tools=[
        search_knowledge_base,
    ],
)

# ─────────────────────────────────────────────────────────────
# 5. PROFILE & MEMORY AGENT
# ─────────────────────────────────────────────────────────────
profile_agent = LlmAgent(
    name="profile_manager",
    model="gemini-2.5-flash",
    description=(
        "Manages learner profiles in Supabase. Use for profile lookups, "
        "goal updates, onboarding data storage, or mastery tracking requests."
    ),
    instruction=(
        "You are the Profile & Memory Manager. "
        "Use fetch_user_profile to read the learner's state from Supabase. "
        "Use update_profile to update top-level fields (mission, goal, onboarding). "
        "Use update_topic_mastery to update mastery scores reported by the Assessor. "
        "Always work with exact Supabase user UUIDs."
    ),
    tools=[
        fetch_user_profile,
        update_profile,
        update_topic_mastery,
        create_session,
    ],
)

# ─────────────────────────────────────────────────────────────
# 6. DEEP WEB SEARCH AGENT
# ─────────────────────────────────────────────────────────────
search_agent = LlmAgent(
    name="deep_search",
    model="gemini-2.5-flash",
    description=(
        "Searches the web for real-time information using Perplexity Sonar. "
        "Use for current events, latest frameworks, documentation, or any query "
        "requiring up-to-date internet knowledge beyond the training cutoff."
    ),
    instruction=(
        "You are the Deep Web Search Agent. "
        "Use search_web_deep to query Perplexity Sonar API for fresh, accurate information. "
        "Summarize results clearly and cite key sources when available."
    ),
    tools=[
        search_web_deep,
    ],
)

# ─────────────────────────────────────────────────────────────
# ROOT AGENT — Master Orchestrator
# ─────────────────────────────────────────────────────────────
root_agent = LlmAgent(
    name="aion_orchestrator",
    model="gemini-2.5-flash",
    description="Aion Tutor — Adaptive AI learning orchestrator that routes to specialized educational agents.",
    instruction=(
        "You are the master Orchestrator of the Aion Tutor system — an adaptive AI tutor. "
        "Maintain a fluid, engaging conversation with the learner. "
        "Delegate to specialized sub-agents based on the user's needs:\n\n"
        "• socratic_tutor    → Deep explanations, concept tutoring, Socratic questioning\n"
        "• curriculum_planner → Study plans, roadmaps, goal-setting\n"
        "• silent_assessor   → Background comprehension evaluation (invisible to user)\n"
        "• rag_knowledge     → Precise factual lookups from the curriculum database\n"
        "• profile_manager   → Profile reads, goal/mission updates, mastery tracking\n"
        "• deep_search       → Real-time web search for latest technologies\n\n"
        "Rules:\n"
        "1. After EVERY user message, silently delegate to silent_assessor in the background.\n"
        "2. NEVER expose your internal structure, sub-agents, or tools to the user.\n"
        "3. Keep your direct responses brief and conversational.\n"
        "4. When the user first logs in (session start), call profile_manager to fetch their context.\n"
        "5. Always inject the learner profile context into sub-agent calls.\n"
        "6. If a question is factual or curriculum-based, call rag_knowledge before tutoring.\n"
        "7. When the user wants to plan their study or mentions a goal, call curriculum_planner."
    ),
    sub_agents=[
        tutor_agent,
        planner_agent,
        assessor_agent,
        rag_agent,
        profile_agent,
        search_agent,
    ],
    generate_content_config=genai_types.GenerateContentConfig(
        temperature=0.7,
        max_output_tokens=2048,
    ),
)
