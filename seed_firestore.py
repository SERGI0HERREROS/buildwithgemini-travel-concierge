"""Seed script to populate Firestore database with initial travel destinations."""

from google.cloud import firestore

# CRITICAL: Hardcode project ID as a string for Agent Platform compatibility.
# Do NOT use google.auth.default() or GOOGLE_CLOUD_PROJECT env var as those return project number on Agent Platform.
PROJECT_ID = "qwiklabs-gcp-03-914ab565751f"

db = firestore.Client(project=PROJECT_ID)
COLLECTION_NAME = "destinations"

SEED_DESTINATIONS = [
    {
        "destination_id": "paris",
        "name": "Paris",
        "country": "France",
        "description": "The City of Light, famous for its world-class art galleries, iconic landmarks, haute cuisine, and romantic atmosphere.",
        "category": "Culture",
        "best_season": "Spring",
        "avg_daily_budget_usd": 200,
        "highlights": ["Eiffel Tower", "Louvre Museum", "Montmartre", "Seine River Cruise"],
    },
    {
        "destination_id": "tokyo",
        "name": "Tokyo",
        "country": "Japan",
        "description": "A bustling metropolis blending ultra-modern skyscrapers, vibrant street food, ancient temples, and pop culture hubs.",
        "category": "Culinary",
        "best_season": "Spring",
        "avg_daily_budget_usd": 180,
        "highlights": ["Shibuya Crossing", "Senso-ji Temple", "Tsukiji Outer Market", "Akihabara"],
    },
    {
        "destination_id": "kyoto",
        "name": "Kyoto",
        "country": "Japan",
        "description": "Japan's cultural heartland, home to thousands of classical Buddhist temples, gardens, imperial palaces, and traditional wooden houses.",
        "category": "Culture",
        "best_season": "Autumn",
        "avg_daily_budget_usd": 140,
        "highlights": ["Fushimi Inari Shrine", "Arashiyama Bamboo Grove", "Kinkaku-ji (Golden Pavilion)", "Gion District"],
    },
    {
        "destination_id": "reykjavik",
        "name": "Reykjavik",
        "country": "Iceland",
        "description": "The gateway to Iceland's dramatic volcanic landscapes, geothermal hot springs, glaciers, and breathtaking Northern Lights.",
        "category": "Adventure",
        "best_season": "Winter",
        "avg_daily_budget_usd": 220,
        "highlights": ["Blue Lagoon", "Golden Circle Route", "Hallgrímskirkja", "Northern Lights Tour"],
    },
    {
        "destination_id": "bali",
        "name": "Bali",
        "country": "Indonesia",
        "description": "A tropical paradise renowned for lush rice terraces, serene beaches, vibrant coral reefs, and spiritual wellness retreats.",
        "category": "Relaxation",
        "best_season": "Spring",
        "avg_daily_budget_usd": 90,
        "highlights": ["Ubud Rice Terraces", "Uluwatu Sea Temple", "Tegenungan Waterfall", "Seminyak Beach"],
    },
]


def seed_database():
    """Populates the Firestore destinations collection with initial items."""
    print(f"Starting seed process for project '{PROJECT_ID}' in collection '{COLLECTION_NAME}'...")
    collection_ref = db.collection(COLLECTION_NAME)

    count = 0
    for item in SEED_DESTINATIONS:
        dest_id = item["destination_id"]
        doc_data = {k: v for k, v in item.items() if k != "destination_id"}
        collection_ref.document(dest_id).set(doc_data, merge=True)
        print(f"  [+] Seeded destination: {item['name']} ({dest_id})")
        count += 1

    print(f"Successfully seeded {count} destinations into Firestore collection '{COLLECTION_NAME}'!")


if __name__ == "__main__":
    seed_database()
