from fastapi import APIRouter, HTTPException

from app.services.anomaly_detection import detect_anomaly

router = APIRouter()


@router.post("/alerts")
def alerts(data: dict):
    try:
        alerts = detect_anomaly(
            rainfall=data.get("rainfall", 0),
            river_flow=data.get("river_flow", 0),
            rolling_flow=data.get("rolling_flow", 0),
            eco_threshold=data.get("eco_threshold")
        )
        return {"alerts": alerts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
