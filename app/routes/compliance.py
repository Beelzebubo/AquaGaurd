from fastapi import APIRouter, HTTPException

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


@router.post("/compliance")
def compliance(data: dict):
    try:
        # Accept both river_flow (frontend) and current_flow (original API)
        current_flow = data.get("river_flow") or data.get("current_flow")
        if current_flow is None:
            raise HTTPException(
                status_code=400,
                detail="Missing required field: river_flow or current_flow"
            )

        # Look up eco_threshold from station_id, or accept it directly
        station_id = data.get("station_id", "").lower()
        eco_threshold = data.get("eco_threshold") or STATION_ECO_THRESHOLDS.get(station_id)
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))