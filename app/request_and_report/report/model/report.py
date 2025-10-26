from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.db import Base

class ReportModel(Base):
    __tablename__ = 'reports'

    id = Column(Integer, primary_key=True, index=True)
    user_name= Column(String, index=True)
    user_email= Column(String, index=True)
    report_details = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
