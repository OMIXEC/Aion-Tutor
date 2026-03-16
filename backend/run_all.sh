#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# Aion Tutor Backend — Startup Script
# Run this from the `backend` directory:  ./run_all.sh
# ═══════════════════════════════════════════════════════════════════════════════

set -e

# Load environment variables
export $(grep -v '^#' .env | xargs)

# Create log directory
mkdir -p logs

echo "🔄 Syncing uv dependencies..."
uv sync

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║       🧠  AION TUTOR BACKEND  —  A2A Multi-Agent System      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Stop previous instances if any
kill $(jobs -p) 2>/dev/null || true
rm -f logs/*.pid

echo "▶  Starting Sub-Agents (A2A Servers)..."

# Launch each sub-agent with its assigned port matching orchestrator_agent.py target_ports
PORT=8001 uv run python -m agents.tutor_agent > logs/tutor.log 2>&1 &
echo $! > logs/tutor.pid

PORT=8002 uv run python -m agents.planner_agent > logs/planner.log 2>&1 &
echo $! > logs/planner.pid

PORT=8003 uv run python -m agents.rag_agent > logs/rag.log 2>&1 &
echo $! > logs/rag.pid

PORT=8004 uv run python -m agents.assessor_agent > logs/assessor.log 2>&1 &
echo $! > logs/assessor.pid

PORT=8005 uv run python -m agents.profile_agent > logs/profile.log 2>&1 &
echo $! > logs/profile.pid

PORT=8007 uv run python -m agents.search_agent > logs/search.log 2>&1 &
echo $! > logs/search.pid

echo "✅ Sub-Agents started (Ports 8001-8007)"

echo "▶  Starting Orchestrator Gateway..."
PORT=${PORT:-8000}
uv run uvicorn agents.orchestrator_agent:app \
    --host 0.0.0.0 \
    --port $PORT \
    --reload \
    --ws websockets \
    --timeout-keep-alive 60 \
    2>&1 | tee logs/orchestrator.log

# When orchestrator stops, kill all background jobs
kill $(jobs -p) 2>/dev/null || true
