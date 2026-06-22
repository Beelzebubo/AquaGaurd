from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.schemas import AlertsRequest
from app.services.anomaly_detection import detect_anomaly

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/alerts")
@limiter.limit("30/minute")
def alerts(data: AlertsRequest, request: Request):
    try:
        alerts_list = detect_anomaly(
            rainfall=data.rainfall,
            river_flow=data.river_flow,
            rolling_flow=data.rolling_flow,
            eco_threshold=data.eco_threshold,
        )
        return {"alerts": alerts_list}
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
