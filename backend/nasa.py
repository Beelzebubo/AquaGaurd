import requests
import pandas as pd

# 1. Define location and time range
# Using 28.63, 81.28 as an example (Karnali River Chisapani)
lat = 28.63
lon = 81.28
start_date = "20260101"
end_date = "20260529"

# 2. Construct the API call
url = "https://power.larc.nasa.gov/api/temporal/daily/point"
params = {
    "parameters": "T2M,RH2M,PRECTOTCORR",
    "community": "ag",
    "longitude": lon,
    "latitude": lat,
    "start": start_date,
    "end": end_date,
    "format": "JSON"
}

response = requests.get(url, params=params)
data = response.json()

param_data = data["properties"]["parameter"]

df = pd.DataFrame(param_data)

print(df.head())

