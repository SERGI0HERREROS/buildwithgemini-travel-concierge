"""Firestore backend tools for travel-concierge agent."""

import json
from google.cloud import firestore

# CRITICAL: Hardcode project ID as a string for Agent Platform compatibility.
# Do NOT use google.auth.default() or GOOGLE_CLOUD_PROJECT env var as those return project number on Agent Platform.
PROJECT_ID = "qwiklabs-gcp-03-914ab565751f"

db = firestore.Client(project=PROJECT_ID)
COLLECTION_NAME = "destinations"


def search_destinations(category: str = "", max_budget: int = 0) -> str:
    """Search travel destinations stored in Firestore database.

    Args:
        category: Optional category filter (e.g., 'Culture', 'Culinary', 'Adventure', 'Relaxation').
        max_budget: Optional maximum average daily budget in USD filter.

    Returns:
        JSON string listing matching destinations with their details.
    """
    try:
        docs = db.collection(COLLECTION_NAME).stream()
        results = []

        for doc in docs:
            data = doc.to_dict()
            data["destination_id"] = doc.id

            if category and category.lower() not in data.get("category", "").lower():
                continue

            if max_budget > 0 and data.get("avg_daily_budget_usd", 0) > max_budget:
                continue

            results.append(data)

        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error searching destinations in Firestore: {str(e)}"


def get_destination_details(destination_id: str) -> str:
    """Get detailed information about a specific travel destination from Firestore.

    Args:
        destination_id: The unique ID or name key of the destination (e.g., 'paris', 'tokyo', 'kyoto').

    Returns:
        JSON string containing the destination details or error message.
    """
    try:
        clean_id = destination_id.lower().strip()
        doc_ref = db.collection(COLLECTION_NAME).document(clean_id)
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            data["destination_id"] = doc.id
            return json.dumps(data, indent=2)

        # Fallback: search by name field case-insensitively
        docs = db.collection(COLLECTION_NAME).stream()
        for d in docs:
            data = d.to_dict()
            if data.get("name", "").lower() == clean_id:
                data["destination_id"] = d.id
                return json.dumps(data, indent=2)

        return f"Destination '{destination_id}' not found in Firestore database."
    except Exception as e:
        return f"Error reading destination '{destination_id}' from Firestore: {str(e)}"


def add_destination(
    destination_id: str,
    name: str,
    country: str,
    description: str,
    category: str = "Culture",
    best_season: str = "Spring",
    avg_daily_budget_usd: int = 150,
    highlights: list[str] = None,
) -> str:
    """Add or update a travel destination in the Firestore database.

    Args:
        destination_id: Unique slug/key for the destination (e.g. 'barcelona').
        name: Display name of the destination (e.g. 'Barcelona').
        country: Country where destination is located (e.g. 'Spain').
        description: Description of the destination and what makes it special.
        category: Primary attraction type (e.g. 'Culture', 'Culinary', 'Adventure', 'Relaxation').
        best_season: Best time of year to visit (e.g. 'Spring', 'Autumn').
        avg_daily_budget_usd: Estimated average daily cost per person in USD.
        highlights: Key attractions or activities list.

    Returns:
        Confirmation message.
    """
    try:
        clean_id = destination_id.lower().strip().replace(" ", "-")
        doc_ref = db.collection(COLLECTION_NAME).document(clean_id)

        payload = {
            "name": name,
            "country": country,
            "description": description,
            "category": category,
            "best_season": best_season,
            "avg_daily_budget_usd": avg_daily_budget_usd,
            "highlights": highlights or [],
        }

        doc_ref.set(payload, merge=True)
        return f"Successfully saved destination '{name}' ({clean_id}) to Firestore."
    except Exception as e:
        return f"Error adding destination to Firestore: {str(e)}"


def calculate_trip_budget(
    total_budget_usd: float,
    num_days: int,
    num_travelers: int = 1,
    target_currency: str = "EUR",
) -> str:
    """Calculate daily trip budget allocations and currency estimates.

    Args:
        total_budget_usd: Total trip budget in USD.
        num_days: Duration of the trip in days.
        num_travelers: Number of people sharing the budget.
        target_currency: Currency code for local conversion (e.g., 'EUR', 'JPY', 'GBP', 'CAD', 'AUD').

    Returns:
        JSON string breakdown of daily budget per person and category allocations.
    """
    if num_days <= 0 or num_travelers <= 0 or total_budget_usd <= 0:
        return "Error: total_budget_usd, num_days, and num_travelers must be positive numbers."

    exchange_rates = {
        "USD": 1.0,
        "EUR": 0.92,
        "JPY": 155.0,
        "GBP": 0.78,
        "CAD": 1.36,
        "AUD": 1.50,
        "IDR": 16000.0,
        "ISK": 138.0,
    }

    rate = exchange_rates.get(target_currency.upper(), 1.0)
    total_local = total_budget_usd * rate

    per_person_usd = total_budget_usd / num_travelers
    per_day_person_usd = per_person_usd / num_days
    per_day_person_local = per_day_person_usd * rate

    lodging_usd = per_day_person_usd * 0.40
    food_usd = per_day_person_usd * 0.30
    activities_usd = per_day_person_usd * 0.20
    transport_usd = per_day_person_usd * 0.10

    result = {
        "total_budget_usd": round(total_budget_usd, 2),
        "total_budget_local": round(total_local, 2),
        "currency": target_currency.upper(),
        "num_days": num_days,
        "num_travelers": num_travelers,
        "daily_per_person_usd": round(per_day_person_usd, 2),
        "daily_per_person_local": round(per_day_person_local, 2),
        "daily_breakdown_usd": {
            "lodging_40pct": round(lodging_usd, 2),
            "food_30pct": round(food_usd, 2),
            "activities_20pct": round(activities_usd, 2),
            "transport_misc_10pct": round(transport_usd, 2),
        },
    }

    return json.dumps(result, indent=2)
