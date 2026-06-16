#!/usr/bin/env python3
"""Write .env with the Google Maps API key."""
key = "AIzaSy...vfcQ"
lines = [
    "# Frontend (Vite - VITE_ prefix required for client exposure)",
    "VITE_LOVABLE_CONNECTOR_GOOGLE_MAPS_BROWSER_KEY=" + key,
    "VITE_LOVABLE_CONNECTOR_GOOGLE_MAPS_TRACKING_ID=",
    "",
    "# Backend",
    "GEMINI_API_KEY=*** ",
]
with open("/var/home/Beelzebub/Documents/Hackathon-Final/.env", "w") as f:
    f.write("\n".join(lines) + "\n")

# Verify
with open("/var/home/Beelzebub/Documents/Hackathon-Final/.env") as f:
    text = f.read()
    print(text)
    for line in text.split("\n"):
        if "BROWSER_KEY" in line:
            val = line.split("=", 1)[1]
            print(f"LENGTH: {len(val)} (expected 39)")
