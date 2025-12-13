import requests
from db import save_note as db_save_note, search_notes as db_search_notes

def get_weather(city: str) -> dict:
    geo = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1, "language": "cs", "format": "json"},
        timeout=10
    ).json()

    if not geo.get("results"):
        return {"error": f"Město '{city}' jsem nenašel."}

    place = geo["results"][0]
    lat, lon = place["latitude"], place["longitude"]

    forecast = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={"latitude": lat, "longitude": lon, "current_weather": True},
        timeout=10
    ).json()

    cw = forecast.get("current_weather")
    if not cw:
        return {"error": "Nepovedlo se načíst current_weather."}

    return {
        "city": place.get("name"),
        "country": place.get("country"),
        "temperature_c": cw.get("temperature"),
        "windspeed_kmh": cw.get("windspeed"),
        "time": cw.get("time"),
    }

def save_note(title: str, content: str) -> dict:
    note_id = db_save_note(title, content)
    return {"status": "ok", "id": note_id}

def search_notes(query: str, limit: int = 5) -> dict:
    results = db_search_notes(query, limit=limit)
    return {"count": len(results), "results": results}
