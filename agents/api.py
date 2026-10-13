"""FastAPI interface for the legacy generic-metric demonstration.

Non-public endpoints require a caller-supplied API key. The endpoint is not
validated for patient care and must not receive identifiable patient data.
"""
import hmac
import os
from typing import Optional
from fastapi import Depends, FastAPI, Header, HTTPException
from .base import AuditLogger, SecurityException
from .models import SystemTaskPayload
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")
app = FastAPI(
    title="Neuromuscular Blockade Agent — legacy audit demonstration",
    description="Unvalidated generic-metric test API. Not clinical decision support.",
    version="2.0.1",
)


def require_api_key(x_api_key: Optional[str] = Header(default=None, alias="X-API-Key")):
    configured = os.getenv("TOF_API_KEY")
    if not configured or len(configured) < 16:
        raise HTTPException(status_code=503, detail="API key is not configured.")
    if not x_api_key or not hmac.compare_digest(x_api_key, configured):
        raise HTTPException(status_code=401, detail="Authentication required.")


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "neuromuscular-blockade-train-of-four-agent",
            "mode": "UNVALIDATED_DEMONSTRATION"}


@app.get("/metrics")
def metrics():
    return {"dossiers_processed_total": len(supervisor.dossier_registry),
            "audit_blocks_total": len(AuditLogger.get_trail()),
            "mode": "UNVALIDATED_DEMONSTRATION"}


@app.post("/api/audit", dependencies=[Depends(require_api_key)])
def api_audit(payload: SystemTaskPayload):
    try:
        dossier = supervisor.process_task(payload)
    except SecurityException:
        raise HTTPException(status_code=400, detail="Input may contain identifying patient data.")
    return {**dossier.to_dict(), "clinical_validation": "NOT_VALIDATED_FOR_PATIENT_CARE"}


@app.post("/api/chat", dependencies=[Depends(require_api_key)])
def api_chat(req: dict):
    query = req.get("query")
    if not isinstance(query, str):
        raise HTTPException(status_code=422, detail="query must be a string")
    try:
        response = supervisor.query_supervisory_chat(query)
    except SecurityException:
        raise HTTPException(status_code=400, detail="Input may contain identifying patient data.")
    return {"response": response, "clinical_validation": "NOT_VALIDATED_FOR_PATIENT_CARE"}


@app.get("/api/audit/logs", dependencies=[Depends(require_api_key)])
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
