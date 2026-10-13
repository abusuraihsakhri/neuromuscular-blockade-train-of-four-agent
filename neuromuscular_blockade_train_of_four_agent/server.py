"""Optional local API: guideline-category TOF interpretation and legacy demonstration."""
import hmac
import os
from typing import Any, Dict, Optional
from .tof import interpret_tof
from .models import ClinicalCasePayload
from .agents import TOFCoordinator

coordinator = TOFCoordinator()


def create_app():
    try:
        from fastapi import Depends, FastAPI, Header, HTTPException
        from pydantic import BaseModel, Field
    except ImportError:
        return None

    app = FastAPI(
        title="Train-of-Four educational interpreter",
        description="Educational TOF categories; not for clinical decision-making or dosing.",
        version="2.0.1",
    )

    def require_api_key(x_api_key: Optional[str] = Header(default=None, alias="X-API-Key")):
        configured = os.getenv("TOF_API_KEY")
        if not configured or len(configured) < 16:
            raise HTTPException(status_code=503, detail="API key is not configured.")
        if not x_api_key or not hmac.compare_digest(configured, x_api_key):
            raise HTTPException(status_code=401, detail="Authentication required.")

    class TOFRequest(BaseModel):
        count: int = Field(..., ge=0, le=4)
        ptc: Optional[int] = Field(default=None, ge=0, le=30)
        ratio: Optional[float] = Field(default=None, ge=0, le=1.5, allow_inf_nan=False)

    class LegacyAuditRequest(BaseModel):
        case_id: str = Field(default="DEMO-001", max_length=128)
        patient_synthetic_id: str = Field(default="SYNTH-DEMO", max_length=128)
        primary_metric: float = Field(default=24.5, allow_inf_nan=False)
        secondary_metric: float = Field(default=14, allow_inf_nan=False)
        status_flag: str = Field(default="NORMAL", max_length=256)
        is_stat: bool = False
        clinical_notes: str = ""
        biomarkers: Dict[str, Any] = Field(default_factory=dict)

    class ChatRequest(BaseModel):
        query: str

    @app.get("/health")
    def health():
        return {"status": "HEALTHY", "mode": "EDUCATIONAL", "version": "2.0.1"}

    @app.post("/api/tof")
    def api_tof(req: TOFRequest):
        try:
            return interpret_tof(req.count, req.ptc, req.ratio)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc))

    @app.post("/api/audit", dependencies=[Depends(require_api_key)])
    def api_audit(req: LegacyAuditRequest):
        case = ClinicalCasePayload(
            case_id=req.case_id, patient_synthetic_id=req.patient_synthetic_id,
            primary_metric=req.primary_metric, secondary_metric=req.secondary_metric,
            status_flag=req.status_flag, is_stat=req.is_stat,
            clinical_notes=req.clinical_notes, biomarkers=req.biomarkers,
        )
        return {**coordinator.process_case(case),
                "clinical_validation": "NOT_VALIDATED_FOR_PATIENT_CARE"}

    @app.post("/api/chat", dependencies=[Depends(require_api_key)])
    def api_chat(req: ChatRequest):
        return {"response": coordinator.query_supervisory_chat(req.query),
                "clinical_validation": "NOT_VALIDATED_FOR_PATIENT_CARE"}

    return app
