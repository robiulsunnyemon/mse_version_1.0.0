from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.db import Base

class NotificationBoxModel(Base):
    __tablename__ = 'notification_box'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    notification_title = Column(String)
    notification_body = Column(String)
    created_at = Column(DateTime(timezone=True), default=func.now())
