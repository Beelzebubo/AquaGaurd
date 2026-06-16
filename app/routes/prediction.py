"""Prediction endpoint — supports both the old 4-feature model
and the new cross-station 7-feature model with NASA POWER live weather.
"""
from fastapi import APIRouter, HTTPException

from app.services.model_service import predict_risk as predict_risk_old
from app.services.cross_station_service import predict_flood_risk
from app.services.nasa_service import fetch_live_weather

router = APIRouter()


@router.post("/predict")
def predict(data: dict):
    """Flood risk prediction.

    Accepts:
      (a) NEW cross-station mode: station_id + temperature + rainfall + humidity
          + river_flow [+ rolling_flow, or live_weather=true]
      (b) OLD 4-feature mode:   temperature + rainfall + humidity + river_flow
          (uses the original Melamchi-trained model)

    When *live_weather=true* the endpoint fetches temperature, rainfall and
    humidity from the NASA POWER API for the station's coordinates, then uses
    the provided river_flow (or the station's P50 flow if none given).
    """
    station_id = data.get("station_id")

    # ── New: cross-station mode ───────────────────────────────────────
    if station_id:
        from app.data.stations import STATIONS
        station = STATIONS.get(station_id)
        if not station:
            raise HTTPException(400, f"Unknown station '{station_id}'")

        temperature = data.get("temperature")
        rainfall    = data.get("rainfall")
        humidity    = data.get("humidity")
        river_flow  = data.get("river_flow")
        rolling     = data.get("rolling_flow")
        use_live    = data.get("live_weather", False)

        # Fetch live NASA POWER weather if requested
        if use_live:
            try:
                live = fetch_live_weather(
                    lat=station["lat"], lng=station["lng"]
                )
                temperature = live["temperature"]
                rainfall    = live["rainfall"]
                humidity    = live["humidity"]
            except Exception as exc:
                raise HTTPException(502, f"NASA POWER fetch failed: {exc}")

        if temperature is None or rainfall is None or humidity is None:
            raise HTTPException(400, "Missing weather inputs (temperature, rainfall, humidity)")
        if river_flow is None:
            raise HTTPException(400, "Missing river_flow")

        result = predict_flood_risk(
            station_id=station_id,
            temperature=float(temperature),
            rainfall=float(rainfall),
            humidity=float(humidity),
            river_flow=float(river_flow),
            rolling_flow=float(rolling) if rolling else None,
        )
        return {
            "predicted_risk": result["probability"],
            "risk_level": result["risk_level"],
            "threshold_flow_m3s": result["threshold_flow_m3s"],
            "threshold_eco_m3s": result["threshold_eco_m3s"],
            "station_flow_stats": result["station_flow_stats"],
        }

    # ── Old: backward-compatible 4-feature mode ───────────────────────
    temperature = data.get("temperature")
    rainfall    = data.get("rainfall")
    humidity    = data.get("humidity")
    river_flow  = data.get("river_flow")

    if temperature is None or rainfall is None or humidity is None or river_flow is None:
        raise HTTPException(400, "Missing required fields: temperature, rainfall, humidity, river_flow")

    features = [[
        float(temperature),
        float(rainfall),
        float(humidity),
        float(river_flow),
    ]]
    prediction = predict_risk_old(features)
    return {"predicted_risk": prediction}
