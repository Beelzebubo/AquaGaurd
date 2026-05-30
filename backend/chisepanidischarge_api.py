import requests

# Example: Chisapani (Karnali) - Coordinates
lat, lon = 28.63, 81.28

# Requesting simulated river discharge
url = f"https://flood-api.open-meteo.com/v1/flood?latitude={lat}&longitude={lon}&daily=river_discharge"
response = requests.get(url)
data = response.json()

print(data)
