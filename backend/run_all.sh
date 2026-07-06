#!/bin/bash

# Aion Tutor Fleet Manager
# Starts all A2A distributed agents and the main orchestrator

# Setup cleanup on exit
trap "kill 0" EXIT

echo "🚀 Starting Aion Tutor A2A Fleet..."

# 1. Start Sub-Agents
echo "📡 Starting Socratic Tutor (8001)..."
uv run python agents/tutor_agent.py &

echo "📡 Starting Curriculum Planner (8002)..."
uv run python agents/planner_agent.py &

echo "📡 Starting RAG Knowledge (8003)..."
uv run python agents/rag_agent.py &

echo "📡 Starting Silent Assessor (8004)..."
uv run python agents/assessor_agent.py &

echo "📡 Starting Profile Manager (8005)..."
uv run python agents/profile_agent.py &

echo "📡 Starting Deep Search (8007)..."
uv run python agents/search_agent.py &

# Wait for agents to initialize
sleep 3

# 2. Start Main Orchestrator
echo "🧠 Starting Orchestrator (8000)..."
uv run python main.py

# Keep script running
wait
