from sqlalchemy import Column, Integer, String, DateTime
from app.db.db import Base
from sqlalchemy.sql import func


class PromotionModel(Base):
    __tablename__ = 'promotions'
    id = Column(Integer, primary_key=True,index=True)
    title = Column(String)
    description = Column(String)
    created_at = Column(DateTime, server_default=func.now())

