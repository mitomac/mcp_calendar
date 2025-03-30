# app/mcp.py

import logging
from datetime import datetime, timedelta, date
from collections import defaultdict
from typing import List, Dict
import httpx
from app.config import settings
from app.models import EventData

logger = logging.getLogger("duke_calendar_mcp")

class CalendarMCP:
    def __init__(self):
        self.api_url = settings.DUKE_CALENDAR_API_URL
        self.debug_mode = settings.DEBUG
        self.event_cache: Dict[str, EventData] = {}
        self.cache_timestamp: datetime = datetime.min
        self.cache_duration = timedelta(hours=1)  # Cache events for 1 hour

    async def ensure_cache_freshness(self):
        if datetime.now() - self.cache_timestamp > self.cache_duration:
            await self.refresh_event_cache()

    async def refresh_event_cache(self, days_ahead: int = 90):
        logger.info("Refreshing event cache from API")
        params = {"future_days": str(days_ahead), "feed_type": "simple"}
        async with httpx.AsyncClient() as client:
            response = await client.get(self.api_url, params=params)
            response.raise_for_status()
            data = response.json()
            events_data = data.get("events", data) if isinstance(data, dict) else data
            self.event_cache = {
                event["id"]: EventData.parse_obj(event)
                for event in events_data if event.get("id")
            }
            self.cache_timestamp = datetime.now()

    async def get_unique_filters_with_ids(self, start_date: date, end_date: date):
        await self.ensure_cache_freshness()
        categories = defaultdict(list)
        groups = defaultdict(list)

        for event in self.event_cache.values():
            if not event.start_timestamp:
                continue
            try:
                event_start = datetime.fromisoformat(event.start_timestamp.replace("Z", "+00:00")).date()
            except Exception as e:
                logger.warning(f"Skipping event {event.id} due to invalid date: {e}")
                continue

            if start_date <= event_start <= end_date:
                if event.categories:
                    for cat in event.categories:
                        categories[cat].append(event.id)
                if event.sponsor:
                    groups[event.sponsor].append(event.id)

        return {
            "categories": dict(categories),
            "groups": dict(groups)
        }

    async def get_events_by_ids(self, event_ids: List[str]) -> List[EventData]:
        await self.ensure_cache_freshness()
        return [
            self.event_cache[event_id]
            for event_id in event_ids if event_id in self.event_cache
        ]

calendar_mcp = CalendarMCP()

