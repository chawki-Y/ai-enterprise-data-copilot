from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_sample_questions() -> None:
    response = client.get("/sample-questions")

    assert response.status_code == 200
    assert "Show trades pending validation" in response.json()


def test_schema_contains_capital_markets_tables() -> None:
    response = client.get("/schema")

    assert response.status_code == 200
    table_names = {table["name"] for table in response.json()["tables"]}
    assert {"trades", "settlements", "counterparties", "books"}.issubset(table_names)
