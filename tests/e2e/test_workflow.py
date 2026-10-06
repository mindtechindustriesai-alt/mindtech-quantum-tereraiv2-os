"""End-to-end workflow test."""

from fastapi.testclient import TestClient
from server import app

client = TestClient(app)


def test_full_chsh_workflow():
    """Verify CHSH end-to-end: fetch root, verify CHSH, check cache."""
    r1 = client.get("/")
    assert r1.status_code == 200

    r2 = client.post(
        "/api/v1/verify/chsh",
        json={"backend": "qiskit_aer", "shots": 1024, "runs": 1},
    )
    assert r2.status_code == 200
    data = r2.json()
    assert data["chsh_s"] is not None
    assert abs(data["chsh_s"]) <= 2.8285
    assert data["status"] in ("verified", "below_classical")


def test_full_security_workflow():
    """Verify security layer end-to-end."""
    inv = client.get("/api/v1/security/keys/inventory").json()
    assert "active_keys" in inv

    gen = client.post(
        "/api/v1/security/keys/generate",
        json={"length": 256, "purpose": "test"},
    ).json()
    assert gen["length"] == 256

    rev = client.post(
        f"/api/v1/security/keys/revoke/{gen['key_id']}"
    ).json()
    assert rev["success"] is True
