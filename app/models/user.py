from sqlalchemy import Column, String, Integer,Boolean,DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.db import Base


class UserModel(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True,index=True)
    uid = Column(String)
    fcmToken = Column(String)
    create_time = Column(DateTime,server_default=func.now())
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now())