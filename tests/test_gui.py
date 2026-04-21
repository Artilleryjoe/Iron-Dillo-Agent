from fastapi.testclient import TestClient

from iron_dillo import gui


def _client() -> TestClient:
    return TestClient(gui.app)


def test_brief_endpoint_returns_content():
    client = _client()
    response = client.post(
        "/api/brief",
        json={
            "scenario": "phishing_concern",
            "business_type": "small business",
            "employee_count_band": "11_50",
            "critical_systems": ["email", "finance"],
            "concern": "Outline a phishing briefing",
            "safeguards": ["mfa"],
            "urgency": "medium",
            "audience": "small_businesses",
            "topic": "identity",
            "include_fact": False,
        },
    )
    payload = response.json()
    assert response.status_code == 200
    assert "## Executive summary" in payload["message"]
    assert payload["brief"]["score"]["value"] >= 0
    assert payload["tool_calls"], "tool list should not be empty"


def test_chat_endpoint_falls_back_without_ollama():
    gui.llm_interface._ollama_module = None
    gui.llm_interface._module_checked = True

    client = _client()
    response = client.post("/api/chat", json={"message": "Summarise ransomware concerns"})
    payload = response.json()

    assert response.status_code == 200
    assert payload["provider"] == "heuristic-brief"
    assert "Local LLM backend unavailable" in payload["response"]
