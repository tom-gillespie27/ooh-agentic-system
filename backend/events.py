import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))

TICKETMASTER_API_KEY = os.getenv("TICKETMASTER_API_KEY")


def get_local_events(lat, lon):

    if not TICKETMASTER_API_KEY:
        return {
            "events": [],
            "summary": "TICKETMASTER_API_KEY missing"
        }

    url = "https://app.ticketmaster.com/discovery/v2/events.json"

    params = {
        "apikey": TICKETMASTER_API_KEY,
        "latlong": f"{lat},{lon}",
        "radius": 10,
        "unit": "miles",
        "size": 5,
        "sort": "date,asc"
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()

        events = []

        for event in (
            data.get("_embedded", {})
                .get("events", [])
        ):
            events.append({
                "name": event.get("name"),
                "date": event.get("dates", {})
                            .get("start", {})
                            .get("localDate"),
                "category": (
                    event.get("classifications", [{}])[0]
                    .get("segment", {})
                    .get("name", "Unknown")
                )
            })

        return {
            "events": events
        }

    except Exception as e:
        return {
            "events": [],
            "summary": str(e)
        }
