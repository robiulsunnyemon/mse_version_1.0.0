from sqlalchemy import Column, String, Integer,ForeignKey
from app.db.db import Base


class FCMTokenModel(Base):
    __tablename__ = 'fcm_tokens'
    id = Column(Integer, primary_key=True,index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    token = Column(String)