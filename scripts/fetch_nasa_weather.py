"""Fetch live weather data for Nepal from NASA POWER API.

Usage:
    python scripts/fetch_nasa_weather.py

Downloads daily precipitation, temperature, humidity & evaporation
for the Nepal bounding box and saves each parameter as a JSON file
in the project root.

NASA POWER is a meteorological reanalysis — it provides weather
variables (rainfall, temperature, humidity), NOT river discharge.
Discharge data comes from historic station CSV files in Datasets/.
"""

import json
import os
import time
from pathlib import Path

import requests

# NASA POWER Daily Regional API endpoint (regional request by bounding box)
BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/regional"

# Hydropower-relevant weather parameters
PARAMETERS = ["PRECTOTCORR", "T2M", "RH2M", "EVAP"]

# Nepal bounding box (min-lat, min-lon, max-lat, max-lon)
NEPAL_BBOX = "26.3,80.0,30.5,88.5"

# Data range — use a recent complete year for reliable data
START = "20240101"
END = "20241231"

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "Datasets" / "nasa_live"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    print(f"Fetching NASA POWER data for Nepal ({START}–{END})\n")

    for param in PARAMETERS:
        print(f"  Requesting {param} …", end=" ", flush=True)

        params = {
            "community": "RE",
            "parameters": param,
            "bbox": NEPAL_BBOX,
            "start": START,
            "end": END,
            "format": "JSON",
        }

        try:
            resp = requests.get(BASE_URL, params=params, timeout=60)
            resp.raise_for_status()
            data = resp.json()

            filename = OUTPUT_DIR / f"nepal_{param.lower()}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print("✓")

        except requests.RequestException as e:
            print(f"✗ {e}")

        time.sleep(3)  # rate-limit courtesy

    print(f"\nDone — files saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
