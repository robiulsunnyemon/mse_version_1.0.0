from typing import Optional
from datetime import datetime
from pydantic import BaseModel,ConfigDict
from typing import List

from app.schemas.event import EventResponse


class RaceBase(BaseModel):
    name: str
    image_logo: str


class RaceCreate(RaceBase):
    serial_number:int
    pass


class RaceUpdate(BaseModel):
    serial_number:Optional[int] # new add
    name: Optional[str] = None
    image_logo: Optional[str] = None


class RaceResponse(RaceBase):
    id: int
    serial_number:int ##new add
    created_at: datetime
    updated_at: datetime
    events: Optional[List[EventResponse]] = []

    model_config = ConfigDict(from_attributes=True)
