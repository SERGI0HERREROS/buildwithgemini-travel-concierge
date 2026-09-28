"""Google Maps tools (Geocoding API & Places API New) for travel-concierge agent."""

import json
import os
import urllib.parse
import urllib.request


def _get_maps_api_key() -> str:
    """Retrieve Google Maps API key from environment variable or local .env file."""
    key = os.getenv("GOOGLE_MAPS_API_KEY")
    if key:
        return key.strip()

    # Fallback to loading .env file in project root or app root
    possible_env_paths = [
        os.path.join(os.path.dirname(__file__), "..", ".env"),
        os.path.join(os.path.dirname(__file__), ".env"),
    ]
    for env_path in possible_env_paths:
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    if line.startswith("GOOGLE_MAPS_API_KEY="):
                        return line.strip().split("=", 1)[1].strip('"\' ')
    return ""


def geocode_address(address: str) -> str:
    """Turn an address or landmark name into geographical coordinates using Google Maps Geocoding API.

    Args:
        address: The address, city, or landmark name to geocode (e.g., 'Eiffel Tower Paris', '1600 Amphitheatre Pkwy').

    Returns:
        JSON string containing the formatted address and location coordinates (latitude, longitude).
    """
    try:
        api_key = _get_maps_api_key()
        if not api_key:
            return "Error: GOOGLE_MAPS_API_KEY environment variable is not set."

        encoded_address = urllib.parse.quote(address)
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"

        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())

        if data.get("status") != "OK" or not data.get("results"):
            return f"Geocoding failed for address '{address}': {data.get('status', 'ZERO_RESULTS')}"

        first_result = data["results"][0]
        loc = first_result["geometry"]["location"]

        result = {
            "name": address,
            "address": first_result.get("formatted_address"),
            "location": {
                "latitude": loc.get("lat"),
                "longitude": loc.get("lng"),
            },
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return f"Error geocoding address '{address}': {str(e)}"


def find_nearby_places(
    latitude: float,
    longitude: float,
    place_type: str = "restaurant",
    radius_meters: float = 1000.0,
) -> str:
    """Find nearby places of a given type around coordinates using Google Maps Places API (New).

    Args:
        latitude: Latitude coordinate of the center point.
        longitude: Longitude coordinate of the center point.
        place_type: Type of place to search for (e.g., 'restaurant', 'cafe', 'tourist_attraction', 'museum', 'lodging').
        radius_meters: Search radius in meters (default 1000m).

    Returns:
        JSON list of nearby places with key fields (name, address, location).
    """
    try:
        api_key = _get_maps_api_key()
        if not api_key:
            return "Error: GOOGLE_MAPS_API_KEY environment variable is not set."

        url = "https://places.googleapis.com/v1/places:searchNearby"
        payload = {
            "includedTypes": [place_type.lower().strip()],
            "maxResultCount": 5,
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": latitude,
                        "longitude": longitude,
                    },
                    "radius": float(radius_meters),
                }
            },
        }

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location",
        }

        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")

        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())

        places_data = data.get("places", [])
        results = []

        for p in places_data:
            display_name = p.get("displayName", {}).get("text", "")
            formatted_address = p.get("formattedAddress", "")
            location = p.get("location", {})

            results.append({
                "name": display_name,
                "address": formatted_address,
                "location": {
                    "latitude": location.get("latitude"),
                    "longitude": location.get("longitude"),
                },
            })

        return json.dumps(results, indent=2)

    except Exception as e:
        return f"Error searching nearby places: {str(e)}"
