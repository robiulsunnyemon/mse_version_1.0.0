from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class EventBase(BaseModel):
    tv_broadcast_chanel: Optional[str] = ""
    radio_broadcast_chanel: Optional[str] = ""
    location: str
    started_at: datetime


class EventCreate(EventBase):
    race_id: int


class EventUpdate(BaseModel):
    tv_broadcast_chanel: Optional[str] = None
    radio_broadcast_chanel: Optional[str] = None
    location: Optional[str] = None
    started_at: Optional[datetime] = None
    race_id: Optional[int] = None


class EventResponse(EventBase):
    id: int
    race_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
