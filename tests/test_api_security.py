"""API authentication, PHI rejection, and numeric validation smoke tests."""
import pytest
from fastapi.testclient import TestClient
from agents.api import app

client = TestClient(app)
PAYLOAD = {
    "task_id": "EXAMPLE-01", "target_identifier": "DEMO-02",
    "primary_metric": 1.5, "secondary_metric": 2.0,
    "status_descriptor": "NOMINAL", "is_critical_flag": False,
}


def test_api_fails_closed_without_secret(monkeypatch):
    monkeypatch.delenv("TOF_API_KEY", raising=False)
    assert client.post("/api/audit", json=PAYLOAD).status_code == 503
    assert client.get("/api/audit/logs").status_code == 503


def test_api_rejects_unauthorized_requests(monkeypatch):
    monkeypatch.setenv("TOF_API_KEY", "local-tests-only-key-not-production")
    assert client.post("/api/audit", json=PAYLOAD).status_code == 401
    assert client.get("/api/audit/logs", headers={"X-API-Key": "bad"}).status_code == 401


def test_api_authorized_and_no_false_validation_claim(monkeypatch):
    key = "local-tests-only-key-not-production"
    monkeypatch.setenv("TOF_API_KEY", key)
    auth = {"X-API-Key": key}
    response = client.post("/api/audit", json=PAYLOAD, headers=auth)
    assert response.status_code == 200, response.text
    assert response.json()["clinical_validation"] == "NOT_VALIDATED_FOR_PATIENT_CARE"
    assert client.get("/api/audit/logs", headers=auth).status_code == 200


def test_api_phi_rejected_without_internal_trace(monkeypatch):
    key = "local-tests-only-key-not-production"
    monkeypatch.setenv("TOF_API_KEY", key)
    response = client.post(
        "/api/audit", json={**PAYLOAD, "task_id": "MRN-123456"},
        headers={"X-API-Key": key},
    )
    assert response.status_code == 400
    assert "123456" not in response.text


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-Infinity"])
def test_api_rejects_nonfinite_numbers(monkeypatch, value):
    key = "local-tests-only-key-not-production"
    monkeypatch.setenv("TOF_API_KEY", key)
    response = client.post("/api/audit", json={**PAYLOAD, "primary_metric": value},
                           headers={"X-API-Key": key})
    assert response.status_code == 422
