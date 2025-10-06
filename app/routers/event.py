from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.db.db import get_db
from app.models.event import EventModel
from app.schemas.event import EventCreate, EventUpdate, EventResponse


event_router = APIRouter(prefix="/events", tags=["Events"])


# ✅ Get all events
@event_router.get("/", response_model=List[EventResponse], status_code=status.HTTP_200_OK)
async def get_events(db: Session = Depends(get_db)):
    events = db.query(EventModel).all()
    return events


# ✅ Get single event by ID
@event_router.get("/{event_id}", response_model=EventResponse, status_code=status.HTTP_200_OK)
async def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(EventModel).filter(EventModel.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


# ✅ Create event
@event_router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(event: EventCreate, db: Session = Depends(get_db)):
    new_event = EventModel(**event.model_dump())
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event


# ✅ Update event
@event_router.put("/{event_id}", response_model=EventResponse, status_code=status.HTTP_200_OK)
async def update_event(event_id: int, event_update: EventUpdate, db: Session = Depends(get_db)):
    event = db.query(EventModel).filter(EventModel.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    for key, value in event_update.model_dump(exclude_unset=True).items():
        setattr(event, key, value)

    db.commit()
    db.refresh(event)
    return event


# ✅ Delete event
@event_router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(EventModel).filter(EventModel.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    db.delete(event)
    db.commit()
    return {"detail": "Event deleted successfully"}
