# app/routers/calendar.py
import logging
from fastapi import APIRouter, HTTPException
from datetime import date, datetime
from app.mcp.calendar import calendar_mcp
from app.models.calendar import (
    EventsByLocalIdsRequest,
    EventsByLocalIdsResponse,
    SimplifiedEventsResponse
)

logger = logging.getLogger("duke_calendar_mcp")
router = APIRouter(tags=["calendar"])

@router.get("/simplified-events", response_model=SimplifiedEventsResponse)
async def get_simplified_events(start_date: date, end_date: date):
    """Get simplified event objects for the specified date range"""
    try:
        events = await calendar_mcp.get_simplified_events(start_date, end_date)
        return SimplifiedEventsResponse(
            events=events,
            count=len(events),
            date_range={"start": start_date.isoformat(), "end": end_date.isoformat()}
        )
    except Exception as e:
        logger.error(f"Error fetching simplified events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/events-by-local-ids", response_model=EventsByLocalIdsResponse)
async def events_by_local_ids(request: EventsByLocalIdsRequest):
    """Get full event details using local IDs"""
    try:
        events = await calendar_mcp.get_events_by_local_ids(request.local_ids)
        return EventsByLocalIdsResponse(events=events, count=len(events))
    except Exception as e:
        logger.error(f"Error fetching events by local IDs: {e}")
        raise HTTPException(status_code=500, detail=str(e))
