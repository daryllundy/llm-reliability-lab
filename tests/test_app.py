from fastapi.testclient import TestClient
from app import app
from unittest.mock import patch

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "llm_request_total" in response.text

@patch("requests.post")
def test_generate_endpoint_success(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"response": "test response"}
    
    response = client.post("/generate", json={"prompt": "test prompt"})
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "latency" in response.json()

@patch("requests.post")
def test_generate_endpoint_failure(mock_post):
    mock_post.side_effect = Exception("Connection error")
    
    response = client.post("/generate", json={"prompt": "test prompt"})
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"
