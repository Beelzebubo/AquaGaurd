import requests

# Melamchi coordinates
lat, lon = 27.83, 85.57

# The API URL
url = f"https://flood-api.open-meteo.com/v1/flood?latitude={lat}&longitude={lon}&daily=river_discharge"

# Make the request
response = requests.get(url)
data = response.json()

# Access the discharge data
print(data)
