"""External API tools for travel-concierge agent."""

import json
import os
import urllib.parse
import urllib.request


def get_live_destination_weather(location: str) -> str:
    """Fetch real-time live weather forecast data for any travel destination worldwide.

    Args:
        location: City or location name (e.g. 'Paris', 'Tokyo', 'Kyoto', 'Reykjavik').

    Returns:
        Formatted summary with real current temperature (°C), wind speed, and location details.
    """
    try:
        # Check if custom API key is set via environment variable
        api_key = os.environ.get("OPENWEATHER_API_KEY") or os.environ.get("WEATHER_API_KEY")

        if api_key:
            # Use OpenWeatherMap if key is provided
            encoded_loc = urllib.parse.quote(location)
            url = f"https://api.openweathermap.org/data/2.5/weather?q={encoded_loc}&appid={api_key}&units=metric"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode())
                temp = data["main"]["temp"]
                desc = data["weather"][0]["description"]
                name = data.get("name", location)
                return f"Live weather in {name}: {temp}°C, {desc}."

        # Default free public API: OpenStreetMap Nominatim + Open-Meteo (No API key required)
        geo_url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(location)}&format=json&limit=1"
        geo_req = urllib.request.Request(geo_url, headers={"User-Agent": "TravelConciergeApp/1.0"})
        with urllib.request.urlopen(geo_req) as resp:
            geo_data = json.loads(resp.read().decode())
            if not geo_data:
                return f"Could not locate destination: '{location}'."
            lat = geo_data[0]["lat"]
            lon = geo_data[0]["lon"]
            display_name = geo_data[0].get("display_name", location)

        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        with urllib.request.urlopen(weather_url) as resp:
            w_data = json.loads(resp.read().decode())
            cw = w_data.get("current_weather", {})
            temp = cw.get("temperature")
            wind = cw.get("windspeed")
            return f"Real-time weather for {display_name}: {temp}°C, wind speed {wind} km/h."

    except Exception as e:
        return f"Error fetching live weather for '{location}': {str(e)}"
