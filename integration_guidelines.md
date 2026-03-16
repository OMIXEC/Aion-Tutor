# Aion Tutor: Frontend & Backend Integration Guidelines

This document outlines the UI/UX flow, architecture, and developer guidelines for fully integrating the Next.js frontend with the Python A2A multi-agent backend. The goal is to evolve the current static templates into an adaptive, personalized learning platform for the hackathon demo.

## 1. UI/UX Flow & Screens

### 1.1 Screen 1: Welcome & Auth (Quick Onboarding)
- **Goal:** Get the user into the system instantly while collecting a base identity for personalization.
- **UI:** A sleek space-themed welcome screen.
- **Integration:** Use **Supabase** for zero-friction Authentication.
  - Providers: Google SSO, GitHub SSO (and Apple if possible, but prioritize Google/GitHub for developers/students).
- **Backend Touchpoint:** Upon first login, Supabase fires a webhook (or frontend makes a `POST /api/user/init` call) to the `orchestrator` to create a blank Profile context in Firestore.

### 1.2 Screen 2: Adaptive Onboarding (Goal & Mission)
- **UI:** A conversational or highly interactive form.
- **Data Points Collected:**
  - What do they want to learn? (e.g., "Azure AI", "Rust Programming" or "Quantum Physics")
  - What is their ultimate mission? (e.g., "Pass the AI-102 exam in 3 weeks", "Build my own startup")
  - (Optional) LinkedIn Profile link to auto-parse background via Tavily/Gemini.
- **Backend Touchpoint:** 
  - Frontend sends data to the `Profile Agent` via the Orchestrator.
  - The `Planner Agent` immediately generates a personalized curriculum.

### 1.3 Screen 3: The Dashboard / Main Learning Arena
- **Current Layout:** The `app/page.tsx` currently has Chat on the left, Progress on the right.
- **Proposed Update Layout:**
  - **Left/Center:** Immersive Chat/Video Interface.
    - Supports Text, Voice, and Video generation streams.
    - An avatar, wave-form, or live-video stream on the side to make it feel human (powered by Gemini Live WebSockets).
  - **Right Sidebar:** Adaptive, real-time Progress Dashboard & Internal Plan View. 
    - The stats update seamlessly as the `Assessor Agent` silently evaluates the user's comprehension through conversation.

---

## 2. Real-time Data Streams (Voice, Video, Text)

To achieve the "WOW" factor for the hackathon, the interaction must feel alive.

### 2.1 WebSockets & Gemini Live APIs
- Modify the `orchestrator_agent` to support WebSockets, not just the REST `/chat` route.
- The frontend Next.js App will connect via `ws://localhost:8000/ws/session/{session_id}`.
- **Text:** Streams token-by-token.
- **Voice:** The system supports STT (Speech to Text) on the frontend if needed, or streams raw audio byte-arrays to the backend, which parses it, computes response, and returns audio hashes (TTS) using Gemini Live API.
- **Video:** Placeholder/Gen-AI video stream of the "Tutor" reacting, or at least a highly responsive visualizer syncing to the audio output.

---

## 3. Frontend Implementation Guidelines (React/Next.js)

### State Management
- Use `zustand` or React Context to hold the global state of the user's progress and current topic. 
- The data should not be static; it must eagerly listen to changes broadcasted by the WebSocket.

### Authentication Code Stub
Setup Supabase quickly:
`npm install @supabase/supabase-js`

```javascript
import { createClient } from '@supabase/supabase-js'

export const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
)

// UI triggers this
const loginWithGoogle = async () => {
  await supabase.auth.signInWithOAuth({ provider: 'google' })
}
```

### WebSocket Integration
Change `ChatInterface` to stream responses:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if(data.type === 'token') {
        appendMessageToken(data.token);
    } else if (data.type === 'progress_update') {
        updateProgressDashboard(data.payload);
    }
}
```

---

## 4. Backend Implementation Guidelines (FastAPI/Python)

### Upgrading the Orchestrator
Currently, `orchestrator_agent.py` uses HTTP POST. We need to mount a WebSocket endpoint.

```python
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # 1. Parse JSON from Frontend (includes audio/text choice)
            req_data = json.loads(data)
            
            # 2. Orchestrate Agents (Tutor, Planner, Assessor)
            # 3. Stream back partial text tokens and progress triggers
            await websocket.send_text(json.dumps({"type": "token", "token": "Hello"}))
            
    except WebSocketDisconnect:
        print("Client disconnected")
```

### Adaptive Data Triggers
When the `Assessor Agent` determines the user has leveled up in understanding, it should notify the Orchestrator. The Orchestrator then pushes a `progress_update` event down the WebSocket. This causes the right-hand Dashboard on the frontend to slide/animate to a master status!

## 5. Summary of Next Steps for Developers
1. **Set up Supabase:** Add keys to frontend `.env` and wire the Next.js auth logic.
2. **Build Onboarding Screen:** Replace the hardcoded templates with an input form capturing "Goal/Mission". Post to backend to generate Profile.
3. **Migrate REST to WebSockets:** Convert `ChatInterface` and FastAPI Orchestrator to full duplex WebSocket communication.
4. **Wire the Progress UI:** Connect the visual progress bars to real JSON emitted by the `Assessor` and `Planner` agents over the line.
