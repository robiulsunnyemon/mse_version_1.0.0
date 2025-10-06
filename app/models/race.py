from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from app.db.db import Base


class RaceModel(Base):
    __tablename__ = 'races'
    id = Column(Integer, primary_key=True,index=True)
    name = Column(String)
    image_logo = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    events = relationship("EventModel", back_populates="race", cascade="all, delete-orphan")
    notifications=relationship("NotificationModel", back_populates="race", cascade="all, delete-orphan")