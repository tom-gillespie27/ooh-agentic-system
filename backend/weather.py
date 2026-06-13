import os
import requests

OPENWEATHER_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_weather(lat, lon):
    if not OPENWEATHER_KEY:
        return {
            "lat": lat,
            "lon": lon,
            "temp": 72,
            "condition": "Unknown",
            "description": "OPENWEATHER_API_KEY is missing."
        }

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_KEY,
        "units": "imperial"
    }
    resp = requests.get(url, params=params, timeout=10)
    data = resp.json()

    main = data.get("main")
    weather_list = data.get("weather")
    if resp.status_code != 200 or not main or not weather_list:
        return {
            "lat": lat,
            "lon": lon,
            "temp": 72,
            "condition": "Unknown",
            "description": f"Weather fetch failed: {data.get('message', resp.text)}"
        }

    return {
        "lat": lat,
        "lon": lon,
        "temp": main.get("temp", 72),
        "condition": weather_list[0].get("main", "Unknown"),
        "description": weather_list[0].get("description", "No description")
    }
