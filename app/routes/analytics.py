"""Analytics Route Module

Provides an aggregated endpoint for flood-risk forecasting,
ESG scoring, hydropower potential estimation, and AI-generated summaries.
"""
from fastapi import APIRouter, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.schemas import AnalyticsRequest
from app.services.scoring import calculate_esg_score
from app.services.risk_forecasting import forecast_risk
from app.services.hydropower import estimate_potential
from app.services.gemini_service import generate_compliance_summary

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/analytics")
@limiter.limit("10/minute")
def analytics(data: AnalyticsRequest, request: Request):
    # --- Forecast risk ---
    rainfall = data.rainfall
    humidity = data.humidity
    temperature = data.temperature
    river_flow = data.river_flow
    station_id = data.station_id

    forecast = forecast_risk(rainfall, humidity, temperature)

    # --- ESG score ---
    compliance_score = data.compliance_score
    anomaly_detected = data.anomaly_detected
    esg_score = calculate_esg_score(compliance_score, anomaly_detected)

    # --- Hydropower potential ---
    head_height = data.head_height
    hydro = estimate_potential(
        river_flow=river_flow,
        head_height=head_height,
        station_id=station_id,
    )

    # --- Gemini summary (optional) ---
    summary_payload = {
        "river_flow": river_flow,
        "rainfall": rainfall,
        "humidity": humidity,
        "compliance_score": compliance_score,
    }
    summary = generate_compliance_summary(summary_payload)

    return {
        "forecast": forecast,
        "esg_score": esg_score,
        "hydropower": hydro,
        "ai_summary": summary,
    }
