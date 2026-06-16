"""Station metadata for the backend — mirrors frontend/data/stations.ts.

Each station has lat/lng coordinates (for NASA POWER fetch), eco threshold,
and capacity (for hydropower calc).
"""
STATIONS = {
    "chisapani":      {"name": "Chisapani",       "river": "Karnali",   "lat": 28.6447, "lng": 81.2731, "ecoThreshold": 280,  "capacityMw": 10800},
    "upper-tamakoshi":{"name": "Upper Tamakoshi",  "river": "Tamakoshi","lat": 27.8333, "lng": 86.1833, "ecoThreshold": 35,   "capacityMw": 456},
    "melamchi":       {"name": "Melamchi",         "river": "Indrawati","lat": 27.8333, "lng": 85.5667, "ecoThreshold": 12,   "capacityMw": 30},
    "kulekhani":      {"name": "Kulekhani I",      "river": "Bagmati",  "lat": 27.5667, "lng": 85.1667, "ecoThreshold": 8,    "capacityMw": 60},
    "kali-gandaki-a": {"name": "Kali Gandaki A",   "river": "Gandaki",  "lat": 27.9833, "lng": 83.5833, "ecoThreshold": 95,   "capacityMw": 144},
    "marsyangdi":     {"name": "Middle Marsyangdi","river": "Marsyangdi","lat": 28.2667,"lng": 84.4,    "ecoThreshold": 45,   "capacityMw": 70},
    "trishuli":       {"name": "Trishuli 3A",      "river": "Trishuli", "lat": 27.9167, "lng": 85.15,   "ecoThreshold": 38,   "capacityMw": 60},
    "arun-iii":       {"name": "Arun III",         "river": "Arun",     "lat": 27.4833, "lng": 87.2333, "ecoThreshold": 120,  "capacityMw": 900},
    "sapta-koshi":    {"name": "Sapta Koshi HM",   "river": "Koshi",    "lat": 26.8617, "lng": 87.1494, "ecoThreshold": 320,  "capacityMw": 3000},
    "budhi-gandaki":  {"name": "Budhi Gandaki",    "river": "Gandaki",  "lat": 28.0167, "lng": 84.8,    "ecoThreshold": 110,  "capacityMw": 1200},
}
