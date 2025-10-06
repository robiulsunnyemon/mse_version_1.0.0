from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.db import Base

class EventModel(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True, index=True)
    race_id = Column(Integer, ForeignKey('races.id', ondelete='CASCADE'))
    tv_broadcast_chanel = Column(String, default='')
    radio_broadcast_chanel = Column(String, default='')
    location = Column(String)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    started_at = Column(DateTime(timezone=True))

    race = relationship("RaceModel", back_populates="events")
