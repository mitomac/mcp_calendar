# app/mcp.py

import logging
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional
import httpx
from app.config import settings
from app.models import EventData, SimplifiedEvent

logger = logging.getLogger("duke_calendar_mcp")

class CalendarMCP:
    def __init__(self):
        self.api_url = settings.DUKE_CALENDAR_API_URL
        self.debug_mode = settings.DEBUG
        self.event_cache: Dict[str, EventData] = {}
        self.cache_timestamp: datetime = datetime.min
        self.cache_duration = timedelta(hours=1)  # Cache events for 1 hour
        self.next_local_id = 1
        self.local_id_to_real_id: Dict[int, str] = {}
        self.real_id_to_local_id: Dict[str, int] = {}

    async def ensure_cache_freshness(self):
        """Ensure the event cache is fresh or refresh it"""
        if datetime.now() - self.cache_timestamp > self.cache_duration:
            await self.refresh_event_cache()

    async def refresh_event_cache(self, days_ahead: int = 90):
        """Refresh the event cache from the Duke Calendar API"""
        logger.info("Refreshing event cache from API")
        params = {"future_days": str(days_ahead), "feed_type": "simple"}
        async with httpx.AsyncClient() as client:
            response = await client.get(self.api_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Reset ID mappings
            self.next_local_id = 1
            self.local_id_to_real_id = {}
            self.real_id_to_local_id = {}
            
            # Process events
            events_data = data.get("events", data) if isinstance(data, dict) else data
            self.event_cache = {}
            
            for event in events_data:
                if not event.get("id"):
                    continue
                
                # Assign a local ID
                local_id = self._get_or_create_local_id(event["id"])
                
                # Create EventData with local_id
                event_obj = EventData(
                    **event,
                    local_id=local_id
                )
                
                self.event_cache[event["id"]] = event_obj
            
            self.cache_timestamp = datetime.now()
            logger.info(f"Cache refreshed with {len(self.event_cache)} events and {len(self.local_id_to_real_id)} local IDs")

    def _get_or_create_local_id(self, real_id: str) -> int:
        """Get an existing local ID or create a new one"""
        if real_id in self.real_id_to_local_id:
            return self.real_id_to_local_id[real_id]
        
        local_id = self.next_local_id
        self.next_local_id += 1
        self.local_id_to_real_id[local_id] = real_id
        self.real_id_to_local_id[real_id] = local_id
        return local_id

    def _get_real_id(self, local_id: int) -> Optional[str]:
        """Convert a local ID to a real ID"""
        return self.local_id_to_real_id.get(local_id)

    async def get_events_by_local_ids(self, local_ids: List[int]) -> List[EventData]:
        """Get events by their local IDs"""
        await self.ensure_cache_freshness()
        result = []
        for local_id in local_ids:
            real_id = self._get_real_id(local_id)
            if real_id and real_id in self.event_cache:
                result.append(self.event_cache[real_id])
        return result


    async def get_simplified_events(self, start_date: date, end_date: date) -> List[SimplifiedEvent]:
        """Get simplified event objects for the specified date range"""
        await self.ensure_cache_freshness()
        
        # Filter events for the date range
        events_in_range = []
        for event in self.event_cache.values():
            if not event.start_timestamp:
                continue
            
            try:
                event_start = datetime.fromisoformat(event.start_timestamp.replace("Z", "+00:00")).date()
                if start_date <= event_start <= end_date:
                    events_in_range.append(event)
            except Exception as e:
                logger.warning(f"Skipping event {event.id} due to invalid date: {e}")
                continue
        
        # Create simplified objects
        simplified_events = []
        for event in events_in_range:
            # Clean and truncate description
            description = event.description or ""
            if len(description) > 200:
                description = description[:200] + "..."
            
            # Create simplified event without location
            simplified = SimplifiedEvent(
                local_id=event.local_id or self._get_or_create_local_id(event.id),
                title=event.summary or "",
                groups=event.sponsor or "",
                categories=event.categories or [],
                description=description,
                start_time=event.start_timestamp
            )
            simplified_events.append(simplified)
        
        return simplified_events

calendar_mcp = CalendarMCP()
