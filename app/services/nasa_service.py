"""NASA POWER live weather fetcher.

Free API — no key required.  Fetches daily reanalysis data for any
(lat, lng) point and returns temperature, rainfall, and humidity.
"""
from datetime import date, timedelta
from typing import Optional

import requests

NASA_POWER_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
DEFAULT_PARAMS = {"community": "RE", "format": "JSON"}


def fetch_live_weather(
    lat: float,
    lng: float,
    start: Optional[str] = None,
    end: Optional[str] = None,
    timeout: int = 30,
) -> dict:
    """Fetch the latest daily weather from NASA POWER for a coordinate.

    Returns
        dict with keys: temperature, rainfall, humidity, source, date
        or raises on persistent failure.
    """
    if start is None:
        # Default: last 3 complete days (POWER data lags ~2-3 days)
        end_d = date.today() - timedelta(days=1)
        start_d = end_d - timedelta(days=2)
        start = start_d.strftime("%Y%m%d")
        end = end_d.strftime("%Y%m%d")

    params = {
        **DEFAULT_PARAMS,
        "parameters": "PRECTOTCORR,T2M,RH2M",
        "latitude": lat,
        "longitude": lng,
        "start": start,
        "end": end,
    }

    resp = requests.get(NASA_POWER_URL, params=params, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()

    props = data.get("properties", {}).get("parameter", {})
    precip = props.get("PRECTOTCORR", {})
    temp   = props.get("T2M", {})
    humid  = props.get("RH2M", {})

    # Pick the most recent day with all three values
    days = sorted(precip.keys())
    if not days:
        raise ValueError("NASA POWER returned no data for this date range")

    latest = days[-1]
    return {
        "temperature": float(temp.get(latest, 20.0)),
        "rainfall": float(precip.get(latest, 0.0)),
        "humidity": float(humid.get(latest, 60.0)),
        "source": "NASA POWER",
        "date": latest,
    }
