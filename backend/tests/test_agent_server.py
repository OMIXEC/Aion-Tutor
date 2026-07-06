from types import SimpleNamespace

from fastapi.testclient import TestClient

from agents.server import APP_NAME, create_agent_app


class FakeSessionService:
    def __init__(self):
        self.created_sessions = []

    async def get_session(self, *, app_name, user_id, session_id, config=None):
        return None

    async def create_session(self, *, app_name, user_id, session_id, state=None):
        self.created_sessions.append(
            {"app_name": app_name, "user_id": user_id, "session_id": session_id}
        )
        return SimpleNamespace(app_name=app_name, user_id=user_id, id=session_id)


class FakeRunner:
    def __init__(self):
        self.session_service = FakeSessionService()
        self.calls = []

    async def run_async(self, *, user_id, session_id, new_message):
        self.calls.append(
            {
                "user_id": user_id,
                "session_id": session_id,
                "new_message": new_message,
            }
        )
        yield SimpleNamespace(
            content=SimpleNamespace(parts=[SimpleNamespace(text="agent reply")]),
            partial=False,
        )


def test_agent_health_endpoint_returns_agent_id():
    runner = FakeRunner()
    client = TestClient(create_agent_app("test_agent", "Test Agent", runner))

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "agent": "test_agent"}


def test_execute_creates_session_and_invokes_runner_with_content():
    runner = FakeRunner()
    client = TestClient(create_agent_app("test_agent", "Test Agent", runner))

    response = client.post(
        "/execute",
        json={"user_id": "user-1", "session_id": "session-1", "content": "hello"},
    )

    assert response.status_code == 200
    assert response.json() == {"reply": "agent reply", "agent_id": "test_agent"}
    assert runner.session_service.created_sessions == [
        {"app_name": APP_NAME, "user_id": "user-1", "session_id": "session-1"}
    ]
    assert len(runner.calls) == 1
    call = runner.calls[0]
    assert call["user_id"] == "user-1"
    assert call["session_id"] == "session-1"
    assert call["new_message"].role == "user"
    assert call["new_message"].parts[0].text == "hello"
