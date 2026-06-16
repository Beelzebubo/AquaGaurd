"""Analytics Route Module

Provides an aggregated endpoint for flood-risk forecasting,
ESG scoring, hydropower potential estimation, and AI-generated summaries.
"""
from fastapi import APIRouter, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.services.scoring import calculate_esg_score
from app.services.risk_forecasting import forecast_risk
from app.services.hydropower import estimate_potential
from app.services.gemini_service import generate_compliance_summary

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/analytics")
@limiter.limit("10/minute")
def analytics(data: dict, request: Request):
    # --- Forecast risk (tolerate missing keys) ---
    rainfall = data.get("rainfall", 0)
    humidity = data.get("humidity", 50)
    temperature = data.get("temperature", 20)
    river_flow = data.get("river_flow", data.get("riverFlow", 1.0))
    station_id = data.get("station_id", data.get("stationId", "melamchi"))

    forecast = forecast_risk(rainfall, humidity, temperature)

    # --- ESG score (tolerate missing keys) ---
    compliance_score = data.get("compliance_score", data.get("complianceScore", 80))
    anomaly_detected = data.get("anomaly_detected", data.get("anomalyDetected", False))
    esg_score = calculate_esg_score(compliance_score, anomaly_detected)

    # --- Hydropower potential ---
    head_height = data.get("head_height", data.get("headHeight"))
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
