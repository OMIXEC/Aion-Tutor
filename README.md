# Aion Cognitive Tutor — Developer Deployment Guide

This repository contains an advanced A2A MCP Agent implementation built on "full bulletproof AI agent" architecture. 
The system features 8 distinct microservices including an Orchestrator, a Socratic Tutor natively using Spaced Repetition/Feynman techniques, a Silent Assessor for background evaluations, and a Search Agent with hybrid Google Search / Perplexity Sonar integration.

## 1. Directory Structure
- `/backend`: The A2A Agent Fleet (FastAPI) and MCP Server (8 Microservices).
- `/frontend`: The Next.js 15 Full-Stack React Application (Shadcn UI).

## 2. Start the Backend Fleet
Ensure you have `python 3.11+` and `uv` installed.
```bash
cd backend

# Install dependencies and build project packages
uv sync

# Duplicate .env.example -> .env and add API Keys
cp .env.example .env

# Run the 8 microservices (Orchestrator, Planner, Tutor, Profiler, Assessor, RAG, Search, MCP)
uv run bash run_all.sh
```

## 3. Start the Frontend
The frontend uses Next.js and Shadcn UI components.
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000` to interact with the Aion Tutor Gateway.
