"""Integration tests for the FastAPI app."""

from fastapi.testclient import TestClient
from server import app

client = TestClient(app)


def test_root_returns_service_info():
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "MQOS TERERAI v2.1"
    assert "chsh_s" in data


def test_health_endpoint():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_apps_moleculemind():
    r = client.get("/api/v1/apps/moleculemind/status")
    assert r.status_code == 200
    assert r.json()["app"] == "MoleculeMind"


def test_apps_mindcell():
    r = client.get("/api/v1/apps/mindcell/status")
    assert r.status_code == 200
    assert r.json()["app"] == "MindCell"


def test_security_status():
    r = client.get("/api/v1/security/status")
    assert r.status_code == 200
    assert r.json()["layer"] == "Quantum Security"


def test_backends_endpoint():
    r = client.get("/api/v1/backends")
    assert r.status_code == 200
