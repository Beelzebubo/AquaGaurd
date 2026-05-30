"""
Analytics Route Module
Provides an aggregated endpoint for environmental forecasting, 
ESG (Environmental, Social, and Governance) scoring, and AI-generated summaries.
"""
from fastapi import APIRouter

from app.services.scoring import calculate_esg_score
from app.services.risk_forecasting import forecast_risk
from app.services.gemini_service import (
    generate_compliance_summary
)
# init the router for analytical related service
router = APIRouter()


@router.post("/analytics")
def analytics(data: dict):

    # Predict environmental risks based on weather parameters
    forecast = forecast_risk(
        data["rainfall"],
        data["humidity"],
        data["temperature"]
    )

    # Calculate the ESG score based on current compliance and detected anomalies basically kati chai intrenational standards 
    # sanga match garxa herxa
    esg_score = calculate_esg_score(
        data["compliance_score"],
        data["anomaly_detected"]
    )

    # Leverage Gemini AI to generate a natural language summary of the current hydrological state
    summary = generate_compliance_summary({
        "river_flow": data["river_flow"],
        "rainfall": data["rainfall"],
        "humidity": data["humidity"],
        "compliance_score": data["compliance_score"]
    })

    return {
        "forecast": forecast,
        "esg_score": esg_score,
        "ai_summary": summary
    }