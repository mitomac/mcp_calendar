# app/routers/calendar.py
import logging
from fastapi import APIRouter, HTTPException
from datetime import date
from app.mcp import calendar_mcp
from app.models import (
    FiltersWithIdsResponse,
    EventsByIdsRequest,
    EventsByIdsResponse
)

logger = logging.getLogger("duke_calendar_mcp")
router = APIRouter(prefix="/calendar", tags=["calendar"])

@router.get("/filters-with-ids", response_model=FiltersWithIdsResponse)
async def filters_with_ids(start_date: date, end_date: date):
    try:
        filters = await calendar_mcp.get_unique_filters_with_ids(start_date, end_date)
        return filters
    except Exception as e:
        logger.error(f"Error fetching filters: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/events-by-ids", response_model=EventsByIdsResponse)
async def events_by_ids(request: EventsByIdsRequest):
    try:
        events = await calendar_mcp.get_events_by_ids(request.ids)
        #events = await calendar_mcp.get_events_by_ids(request.event_ids)
        return EventsByIdsResponse(events=events, count=len(events))
    except Exception as e:
        logger.error(f"Error fetching events by IDs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


