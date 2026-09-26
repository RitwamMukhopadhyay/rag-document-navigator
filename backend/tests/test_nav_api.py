import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "Document Navigator" in data["service"]

def test_retrieve_endpoint():
    payload = {
        "question": "What is the return window for most products?",
        "top_k": 3,
        "chunk_size": 600,
        "overlap": 80
    }
    res = client.post("/api/retrieve", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "retrieved_chunks" in data

def test_agent_run_endpoint():
    payload = {
        "question": "Name two accepted payment methods.",
        "top_k": 5,
        "chunk_size": 600,
        "overlap": 80
    }
    res = client.post("/api/agent/run", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert "retrieval_trace" in data
    assert len(data["retrieval_trace"]) >= 5

def test_eval_questions_endpoint():
    res = client.get("/api/eval/questions")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 15
    assert data[0]["id"] == "Q01"
