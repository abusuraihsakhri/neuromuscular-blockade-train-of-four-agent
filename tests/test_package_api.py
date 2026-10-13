"""Optional package API boundary and access-control tests."""
import pytest
from fastapi.testclient import TestClient
from neuromuscular_blockade_train_of_four_agent.server import create_app

client = TestClient(create_app())


def test_package_tof_api():
    response = client.post("/api/tof", json={"count": 4, "ratio": 0.9})
    assert response.status_code == 200
    assert response.json()["category"] == "RECOVERED"
    assert client.post("/api/tof", json={"count": 0, "ptc": 0}).json()["category"] == "COMPLETE"


@pytest.mark.parametrize("payload", [
    {"count": 5}, {"count": 0, "ratio": 0.9}, {"count": 4, "ptc": 2},
    {"count": 4, "ratio": "NaN"},
])
def test_package_tof_invalid_payload(payload):
    assert client.post("/api/tof", json=payload).status_code == 422


def test_package_legacy_audit_restricted(monkeypatch):
    monkeypatch.delenv("TOF_API_KEY", raising=False)
    assert client.post("/api/audit", json={}).status_code == 503
    monkeypatch.setenv("TOF_API_KEY", "secure-local-tests-key-123")
    assert client.post("/api/audit", json={}).status_code == 401
    response = client.post("/api/audit", json={}, headers={"X-API-Key": "secure-local-tests-key-123"})
    assert response.status_code == 200
    assert response.json()["clinical_validation"] == "NOT_VALIDATED_FOR_PATIENT_CARE"
