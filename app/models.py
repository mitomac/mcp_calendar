# app/models.py

from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class EventLocation(BaseModel):
    address: Optional[str] = None
    link: Optional[str] = None


class EventContact(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class EventData(BaseModel):
    id: str
    start_timestamp: str
    end_timestamp: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    sponsor: Optional[str] = None
    co_sponsors: Optional[List[str]] = None
    location: Optional[EventLocation] = None
    contact: Optional[EventContact] = None
    categories: Optional[List[str]] = None
    link: Optional[str] = None
    event_url: Optional[str] = None

    class Config:
        extra = "allow"


class CalendarQuery(BaseModel):
    query: str
    time_range: str = "today"
    groups: Optional[List[str]] = None
    categories: Optional[List[str]] = None


class CalendarResponse(BaseModel):
    events: List[EventData]
    message: str
    debug_info: Optional[Dict[str, Any]] = None


class ReferenceData(BaseModel):
    data: List[str]


class EventsByIdsRequest(BaseModel):
    ids: List[str]


class EventsByIdsResponse(BaseModel):
    events: List[EventData]


class FiltersWithIdsResponse(BaseModel):
    categories: Dict[str, List[str]]
    groups: Dict[str, List[str]]

