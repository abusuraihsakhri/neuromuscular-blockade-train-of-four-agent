"""
Automated Pytest Test Suite for Neuromuscular Blockade Train Of Four Agent.
Domain: Clinical & Biomedical AI
Standard: CAP / CLSI / ISO Standards
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import PHIGuard, AuditLogger, AuditTrail, SecurityException
from agents.models import SystemTaskPayload, UrgencyLevel, SystemIntegrityStatus
from agents.workers import InvariantQCWorker, SafetyEscalationWorker, ProtocolConformanceWorker
from agents.supervisor import SystemSupervisor
from cli import main


def test_phi_guard_enforcement():
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Patient MRN-994827 blood culture positive for Staphylococcus")

    # Clean text passes
    PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")


def test_phi_guard_redaction():
    """Test that PHI guard can redact sensitive information."""
    text_with_phi = "Patient John Doe, MRN-123456, phone 555-123-4567"
    redacted = PHIGuard.redact_phi(text_with_phi)
    assert "REDACTED_IDENTIFIER" in redacted
    assert "John Doe" not in redacted
    assert "MRN-123456" not in redacted


def test_specialized_workers():
    # Worker 1: QC Invariant
    p1 = SystemTaskPayload(task_id="T1", target_identifier="KEY-01", primary_metric=35.0)
    alerts1 = InvariantQCWorker.evaluate(p1)
    assert len(alerts1) == 1
    assert alerts1[0].urgency == UrgencyLevel.ELEVATED

    # Worker 2: Safety
    p2 = SystemTaskPayload(task_id="T2", target_identifier="KEY-02", primary_metric=10.0, is_critical_flag=True)
    alerts2 = SafetyEscalationWorker.evaluate(p2)
    assert len(alerts2) == 1
    assert alerts2[0].urgency == UrgencyLevel.CRITICAL_STAT

    # Worker 3: Protocol Conformance
    p3 = SystemTaskPayload(task_id="T3", target_identifier="KEY-03", primary_metric=10.0, status_descriptor="DISCORDANT_ANOMALY")
    alerts3 = ProtocolConformanceWorker.evaluate(p3)
    assert len(alerts3) == 1


def test_supervisor_consensus_and_audit():
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(
        task_id="TASK-PROD-01",
        target_identifier="KEY-PROD-01",
        primary_metric=12.0,
        secondary_metric=4.0,
        status_descriptor="NOMINAL"
    )
    dossier = supervisor.process_task(payload)
    assert dossier.overall_urgency == UrgencyLevel.ROUTINE
    assert dossier.integrity_status == SystemIntegrityStatus.VALIDATED
    assert dossier.audit_hash != ""

    # Verify cryptographic audit trail
    assert AuditLogger.verify_integrity() is True

    # CLI tests
    assert main(["audit", "--task-id", "CLI-TEST-01"]) == 0
    assert main(["chat", "Explain", "specifications"]) == 0
    assert main(["verify-audit"]) == 0


def test_audit_trail_integrity_verification():
    """Test that audit trail integrity verification detects tampering."""
    trail = AuditTrail(secret_key="test-key-for-integrity-verification")

    # Log some entries
    entry1 = trail.log("test-actor", "test-tier", "TEST_EVENT", {"data": "value1"})
    entry2 = trail.log("test-actor", "test-tier", "TEST_EVENT", {"data": "value2"})

    # Verify integrity passes for valid trail
    assert trail.verify_integrity() is True

    # Tamper with an entry
    trail.logs[0]["payload_hash"] = "tampered_hash"

    # Verify integrity fails after tampering
    assert trail.verify_integrity() is False


def test_audit_trail_chain_linkage():
    """Test that audit trail chain linkage is properly maintained."""
    trail = AuditTrail(secret_key="test-key-for-chain-linkage")

    entry1 = trail.log("actor1", "tier1", "EVENT_1", {"a": 1})
    entry2 = trail.log("actor2", "tier2", "EVENT_2", {"b": 2})

    # Second entry's prev_hash should equal first entry's current_hash
    assert entry2["prev_hash"] == entry1["current_hash"]

    # First entry's prev_hash should be genesis
    assert entry1["prev_hash"] == "GENESIS_BLOCK_0000000000000000"


def test_batch_missing_input_file():
    """Test that batch command handles missing input file gracefully."""
    result = main(["batch", "-i", "nonexistent_file_xyz.csv"])
    assert result == 1


def test_audit_trail_hmac_signature_verification():
    """Test that HMAC signatures are properly verified."""
    trail = AuditTrail(secret_key="test-key-for-hmac-verification")

    trail.log("actor", "tier", "EVENT", {"key": "value"})

    # Verify integrity (which now includes HMAC signature verification)
    assert trail.verify_integrity() is True

    # Tamper with the signature
    trail.logs[0]["current_hash"] = "invalid_signature"

    # Should fail verification
    assert trail.verify_integrity() is False
