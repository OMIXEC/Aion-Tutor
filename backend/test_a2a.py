import requests
import json
import time

AGENTS = {
    "orchestrator": "http://localhost:8000/health",
    "tutor": "http://localhost:8001/health",
    "planner": "http://localhost:8002/health",
    "rag": "http://localhost:8003/health",
    "assessor": "http://localhost:8004/health",
    "profile": "http://localhost:8005/health",
    "search": "http://localhost:8007/health"
}

def test_fleet():
    print("Testing Aion A2A Fleet Health...")
    for name, url in AGENTS.items():
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                print(f"[OK] {name.upper()}: {resp.json().get('agent', 'N/A')}")
            else:
                print(f"[FAIL] {name.upper()}: Status {resp.status_code}")
        except Exception as e:
            print(f"[ERR] {name.upper()}: {e}")

if __name__ == "__main__":
    time.sleep(2) # Wait for startup
    test_fleet()
