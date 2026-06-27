from fastapi.testclient import TestClient

from app.main import app
from app.api.routes import trade_ops_agent


client = TestClient(app)


def _disable_agent_log_http(monkeypatch) -> None:
    monkeypatch.setattr(trade_ops_agent.client, "post", lambda endpoint, payload: {"id": 1})


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_sample_questions() -> None:
    response = client.get("/sample-questions")

    assert response.status_code == 200
    assert "Show trades pending validation" in response.json()


def test_agent_sample_questions() -> None:
    response = client.get("/agent/sample-questions")

    assert response.status_code == 200
    assert "Give me an operations morning summary." in response.json()


def test_agent_explains_application_without_data_query(monkeypatch) -> None:
    _disable_agent_log_http(monkeypatch)
    response = client.post("/agent/ask", json={"question": "What is this app about?"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["intent"] == "APP_EXPLANATION"
    assert payload["generatedSql"] is None
    assert payload["columns"] == []
    assert payload["rows"] == []
    assert "Trade Operations Management System" in payload["answer"]


def test_agent_explains_trade_concept_without_data_query(monkeypatch) -> None:
    _disable_agent_log_http(monkeypatch)
    response = client.post("/agent/ask", json={"question": "What is a trade?"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["intent"] == "CONCEPT_EXPLANATION"
    assert payload["generatedSql"] is None
    assert payload["rows"] == []
    assert "transaction" in payload["answer"]


def test_agent_logs_interaction_in_trade_operations_system(monkeypatch) -> None:
    captured = {}

    def capture_log(endpoint, payload):
        captured["endpoint"] = endpoint
        captured["payload"] = payload
        return {"id": 1}

    monkeypatch.setattr(trade_ops_agent.client, "post", capture_log)

    response = client.post("/agent/ask", json={"question": "What is this app about?"})

    assert response.status_code == 200
    assert captured["endpoint"] == "/api/ai-copilot/logs"
    assert captured["payload"]["intent"] == "APP_EXPLANATION"
    assert captured["payload"]["data_source_endpoint"] is None
    assert captured["payload"]["row_count"] == 0


def test_schema_contains_capital_markets_tables() -> None:
    response = client.get("/schema")

    assert response.status_code == 200
    table_names = {table["name"] for table in response.json()["tables"]}
    assert {"trades", "settlements", "counterparties", "books"}.issubset(table_names)
