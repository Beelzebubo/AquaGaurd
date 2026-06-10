from fastapi import APIRouter

from app.services.anomaly_detection import detect_anomaly

router = APIRouter()


@router.post("/alerts")
def alerts(data: dict):
    alerts = detect_anomaly(
        data["rainfall"],
        data["river_flow"],
        data["rolling_flow"],
        data.get("eco_threshold")
    )
    return {"alerts": alerts}
