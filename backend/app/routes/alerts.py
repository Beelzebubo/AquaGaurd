from fastapi import APIRouter

# Import the anomaly detection service logic
from app.services.anomaly_detection import (
    detect_anomaly
)

# Initialize router for grouping related modules
router = APIRouter()


@router.post("/alerts")
def alerts(data: dict):
# The data for the parameters rainfall, riverflow and rollingflow are used for detecting anomaly.
    anomaly = detect_anomaly(
        data["rainfall"],
        data["river_flow"],
        data["rolling_flow"]
    )

    alerts = []

    # If the service identifies an anomaly, add the message to the response 
    if anomaly["anomaly"]:
        alerts.append(anomaly["message"])

    return {
        "alerts": alerts
    }