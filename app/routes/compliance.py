from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.schemas import ComplianceRequest
from app.services.compliance_engine import (
    evaluate_ifc_compliance
)

# Eco-thresholds for known Nepal hydropower stations (m³/s)
STATION_ECO_THRESHOLDS = {
    "chisapani": 280,
    "upper-tamakoshi": 35,
    "melamchi": 12,
    "kulekhani": 8,
    "kali-gandaki-a": 95,
    "marsyangdi": 45,
    "trishuli": 38,
    "arun-iii": 120,
    "sapta-koshi": 320,
    "budhi-gandaki": 110,
}

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/compliance")
@limiter.limit("30/minute")
def compliance(data: ComplianceRequest, request: Request):
    try:
        current_flow = data.river_flow if data.river_flow is not None else data.current_flow
        if current_flow is None:
            raise HTTPException(
                status_code=400,
                detail="Missing required field: river_flow or current_flow"
            )

        station_id = data.station_id.lower() if data.station_id else ""
        eco_threshold = data.eco_threshold
        if eco_threshold is None and station_id:
            eco_threshold = STATION_ECO_THRESHOLDS.get(station_id)
        if eco_threshold is None:
            raise HTTPException(
                status_code=400,
                detail="Missing eco_threshold — provide it directly or give a known station_id"
            )

        result = evaluate_ifc_compliance(current_flow, eco_threshold)
        result["station_id"] = station_id
        result["eco_threshold_m3s"] = eco_threshold
        result["current_flow_m3s"] = current_flow
        return result
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
