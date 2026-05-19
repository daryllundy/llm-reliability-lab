from unittest.mock import Mock

import requests
from fastapi.testclient import TestClient

import app as app_module


client = TestClient(app_module.app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_metrics_endpoint_exposes_core_metrics():
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "llm_request_total" in response.text
    assert "llm_request_latency_seconds_bucket" in response.text
    assert "llm_inference_in_flight" in response.text


def test_generate_uses_configured_ollama_url_and_non_streaming(monkeypatch):
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_post = Mock(return_value=mock_response)
    monkeypatch.setattr(app_module.requests, "post", mock_post)
    monkeypatch.setattr(app_module, "OLLAMA_URL", "http://ollama.example/api/generate")

    response = client.post("/generate", json={"prompt": "test prompt"})

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "latency" in response.json()
    mock_post.assert_called_once()
    assert mock_post.call_args.kwargs["json"] == {
        "model": app_module.MODEL,
        "prompt": "test prompt",
        "stream": False,
    }
    assert mock_post.call_args.args[0] == "http://ollama.example/api/generate"
    assert mock_post.call_args.kwargs["timeout"] == 60


def test_generate_uses_configured_model_name(monkeypatch):
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_post = Mock(return_value=mock_response)
    monkeypatch.setattr(app_module.requests, "post", mock_post)
    monkeypatch.setattr(app_module, "MODEL", "llama3.2:3b")

    response = client.post("/generate", json={"prompt": "test prompt"})

    assert response.status_code == 200
    assert mock_post.call_args.kwargs["json"]["model"] == "llama3.2:3b"


def test_generate_timeout_returns_504(monkeypatch):
    monkeypatch.setattr(app_module.requests, "post", Mock(side_effect=requests.Timeout))

    response = client.post("/generate", json={"prompt": "test prompt"})

    assert response.status_code == 504
    assert response.json()["detail"] == "Request timeout"


def test_generate_request_failure_returns_503(monkeypatch):
    monkeypatch.setattr(
        app_module.requests,
        "post",
        Mock(side_effect=requests.ConnectionError("connection failed")),
    )

    response = client.post("/generate", json={"prompt": "test prompt"})

    assert response.status_code == 503
    assert response.json()["detail"] == "Service unavailable"


def test_generate_unexpected_failure_returns_500(monkeypatch):
    monkeypatch.setattr(app_module.requests, "post", Mock(side_effect=RuntimeError("boom")))

    response = client.post("/generate", json={"prompt": "test prompt"})

    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"


def test_generate_rejects_empty_prompt():
    response = client.post("/generate", json={"prompt": ""})

    assert response.status_code == 422


def test_generate_rejects_missing_prompt():
    response = client.post("/generate", json={})

    assert response.status_code == 422


def test_generate_rejects_prompt_over_1000_characters(monkeypatch):
    mock_post = Mock()
    monkeypatch.setattr(app_module.requests, "post", mock_post)

    response = client.post("/generate", json={"prompt": "x" * 1001})

    assert response.status_code == 422
    mock_post.assert_not_called()


def test_generate_resets_in_flight_and_gpu_metrics_after_failure(monkeypatch):
    monkeypatch.setattr(
        app_module.requests,
        "post",
        Mock(side_effect=requests.ConnectionError("connection failed")),
    )

    response = client.post("/generate", json={"prompt": "test prompt"})

    assert response.status_code == 503
    assert app_module.inference_in_flight._value.get() == 0
    assert app_module.gpu_util._value.get() == 0
