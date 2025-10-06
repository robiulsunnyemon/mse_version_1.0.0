from typing import Optional
from datetime import datetime
from pydantic import BaseModel,ConfigDict
from typing import List

from app.schemas.event import EventResponse


class RaceBase(BaseModel):
    name: str
    image_logo: str


class RaceCreate(RaceBase):
    pass


class RaceUpdate(BaseModel):   # Update schema
    name: Optional[str] = None
    image_logo: Optional[str] = None


class RaceResponse(RaceBase):
    id: int
    created_at: datetime
    updated_at: datetime
    events: Optional[List[EventResponse]] = []

    model_config = ConfigDict(from_attributes=True)
