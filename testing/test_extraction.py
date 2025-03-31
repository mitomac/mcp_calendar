import asyncio
from collections import defaultdict
from datetime import datetime, timedelta
import httpx

API_URL = "https://calendar.duke.edu/events/index.json"
FUTURE_DAYS = 90 
FEED_TYPE = "simple"

async def fetch_simple_feed():
    params = {
        "future_days": FUTURE_DAYS,
        "feed_type": FEED_TYPE
    }
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(API_URL, params=params)
        response.raise_for_status()
        return response.json().get("events", [])
def extract_categories_and_sponsors(events, start_date, end_date):
    categories = defaultdict(list)
    sponsors = defaultdict(list)

    for event in events:
        event_id = event.get("id")
        start_str = event.get("start_timestamp")

        if not event_id or not start_str:
            continue

        try:
            event_start = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
        except Exception as e:
            print(f"Skipping bad date for event {event_id}: {e}")
            continue

        if not (start_date <= event_start.date() <= end_date):
            continue

        # Handle categories safely
        event_categories = event.get("categories")
        if isinstance(event_categories, list):
            for category in event_categories:
                categories[category].append(event_id)

        sponsor = event.get("sponsor")
        if sponsor:
            sponsors[sponsor].append(event_id)

    return categories, sponsors

async def main():
    print("Fetching simple feed...")
    events = await fetch_simple_feed()
    today = datetime.utcnow().date()
    end_day = today + timedelta(days=FUTURE_DAYS)

    categories, sponsors = extract_categories_and_sponsors(events, today, end_day)

    print("\nExtracted Categories and their Event IDs:")
    for cat, ids in categories.items():
        print(f"{cat}: {ids}")

    print("\nExtracted Sponsors and their Event IDs:")
    for sponsor, ids in sponsors.items():
        print(f"{sponsor}: {ids}")

if __name__ == "__main__":
    asyncio.run(main())

