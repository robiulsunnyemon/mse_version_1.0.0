from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.db import Base

class RequestModel(Base):
    __tablename__ = 'requests'

    id = Column(Integer, primary_key=True, index=True)
    user_name= Column(String, index=True)
    user_email= Column(String, index=True)
    request_details = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())