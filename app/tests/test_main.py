"""Tests for the observability-lab application."""

from fastapi.testclient import TestClient

from src.app.main import app

client = TestClient(app)


def test_root() -> None:
    body = client.get("/").json()
    assert body["service"] == "observability-lab"


def test_healthz() -> None:
    assert client.get("/healthz").json() == {"status": "healthy"}


def test_work_ok() -> None:
    assert client.get("/work").json() == {"status": "ok"}


def test_work_simulates_failure() -> None:
    # fail=1.0 => always fails
    assert client.get("/work?fail=1.0").status_code == 500


def test_metrics_endpoint_exposes_prometheus_format() -> None:
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text
    assert "# HELP" in response.text


def test_metrics_records_requests() -> None:
    client.get("/healthz")
    text = client.get("/metrics").text
    assert 'endpoint="/healthz"' in text
