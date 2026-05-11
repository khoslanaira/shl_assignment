import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_vague_query():
    payload = {"messages": [{"role": "user", "content": "I want a test."}]}
    response = client.post("/chat", json=payload)
    data = response.json()
    assert data["recommendations"] == []
    assert "?" in data["reply"] # Should ask a clarifying question

def test_java_role():
    payload = {"messages": [{"role": "user", "content": "I'm hiring a Java developer."}]}
    response = client.post("/chat", json=payload)
    data = response.json()
    assert len(data["recommendations"]) > 0
    assert "java" in data["recommendations"][0]["name"].lower()
    assert "shl.com" in data["recommendations"][0]["url"]

def test_turn_cap():
    # 9 messages (5 user, 4 assistant)
    payload = {"messages": [{"role": "user", "content": "hi"}] * 9}
    response = client.post("/chat", json=payload)
    assert response.json()["end_of_conversation"] is True

def test_off_topic():
    payload = {"messages": [{"role": "user", "content": "What is the average salary of a Java dev?"}]}
    response = client.post("/chat", json=payload)
    assert response.json()["recommendations"] == []