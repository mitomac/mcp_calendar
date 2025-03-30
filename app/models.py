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
    local_id: Optional[int] = None
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



class SimplifiedEvent(BaseModel):
    local_id: int
    title: Optional[str] = None
    groups: Optional[str] = None
    categories: Optional[List[str]] = None
    description: Optional[str] = None
    start_time: Optional[str] = None

class SimplifiedEventsResponse(BaseModel):
    events: List[SimplifiedEvent]
    count: int
    date_range: Dict[str, str]


class EventsByLocalIdsRequest(BaseModel):
    local_ids: List[int]


class EventsByLocalIdsResponse(BaseModel):
    events: List[EventData]
    count: int
