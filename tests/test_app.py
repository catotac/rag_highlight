# tests/test_app.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_generate_answer():
    response = client.get("/generate_answer?query=test")
    assert response.status_code == 200
    assert "answer" in response.json()
    assert response.json()["answer"] == "Answer based on query: test"

