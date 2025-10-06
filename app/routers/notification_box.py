from typing import List
from fastapi import APIRouter, Depends, status,HTTPException
from sqlalchemy.orm import Session
from app.models.user import UserModel
from app.db.db import get_db
from app.schemas.notification_box import NotificationBox
from app.models.notification_box import NotificationBoxModel
from app.utils.user_info import get_user_info

notification_box_router = APIRouter(prefix="/notification_box", tags=["NotificationBox"])


@notification_box_router.get("/", response_model=List[NotificationBox], status_code=status.HTTP_200_OK)
def get_notification_box_list(db: Session = Depends(get_db)):
    # সব notification fetch
    notification_box_list = db.query(NotificationBoxModel).all()
    return notification_box_list


@notification_box_router.get("/user/me", response_model=List[NotificationBox], status_code=status.HTTP_200_OK)
def get_notification_box_me(db: Session = Depends(get_db), user: dict = Depends(get_user_info)):
    # Current user info
    uid = user["uid"]
    if not  uid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,)
    db_user = db.query(UserModel).filter(UserModel.uid == uid).first()
    if not db_user:
        return []

    notification_box_list = db.query(NotificationBoxModel).filter(
        NotificationBoxModel.user_id == db_user.id
    ).all()
    return notification_box_list
