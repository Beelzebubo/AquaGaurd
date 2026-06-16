from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.services.anomaly_detection import detect_anomaly

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/alerts")
@limiter.limit("30/minute")
def alerts(data: dict, request: Request):
    try:
        alerts_list = detect_anomaly(
            rainfall=data.get("rainfall", 0),
            river_flow=data.get("river_flow", 0),
            rolling_flow=data.get("rolling_flow", 0),
            eco_threshold=data.get("eco_threshold")
        )
        return {"alerts": alerts_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
