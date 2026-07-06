from typing import Any

from fastapi import FastAPI
from google.genai import types


APP_NAME = "aion-tutor"


def _extract_event_text(event: Any) -> str:
    content = getattr(event, "content", None)
    parts = getattr(content, "parts", None) or []
    texts = [part.text for part in parts if getattr(part, "text", None)]
    return "".join(texts)


async def _ensure_session(session_service: Any, user_id: str, session_id: str) -> None:
    session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
    )
    if session is None:
        await session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
        )


async def _run_agent(runner: Any, user_id: str, session_id: str, message: str) -> str:
    await _ensure_session(runner.session_service, user_id, session_id)
    content = types.Content(role="user", parts=[types.Part(text=message)])

    final_chunks: list[str] = []
    partial_chunks: list[str] = []
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content,
    ):
        text = _extract_event_text(event)
        if not text:
            continue
        if getattr(event, "partial", False):
            partial_chunks.append(text)
        else:
            final_chunks.append(text)

    return "".join(final_chunks or partial_chunks)


def create_agent_app(agent_id: str, title: str, runner: Any) -> FastAPI:
    app = FastAPI(title=title)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "healthy", "agent": agent_id}

    @app.post("/execute")
    async def execute(payload: dict[str, Any]) -> dict[str, str]:
        session_id = str(payload.get("session_id") or "default")
        user_id = str(payload.get("user_id") or "default")
        message = str(payload.get("content") or "")
        reply = await _run_agent(runner, user_id, session_id, message)
        return {"reply": reply, "agent_id": agent_id}

    return app
