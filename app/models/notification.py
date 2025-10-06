from sqlalchemy import Column, Integer,DateTime,ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.db import Base



class NotificationModel(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    notification_hour=Column(Integer)
    race_id=Column(Integer, ForeignKey('races.id', ondelete='CASCADE'))
    created_at = Column(DateTime, server_default=func.now())

    race = relationship('RaceModel', back_populates='notifications')
