from fastapi import APIRouter, Depends, HTTPException,status
from app.schemas.user import UserCreate, UserRead
from app.db.db import get_db
from app.models.user import UserModel
from sqlalchemy.orm import Session
from app.utils.token_generation import create_access_token
from app.utils.user_info import get_user_info
from app.models.fcm_token import FCMTokenModel
from typing import List



router = APIRouter(prefix="/user", tags=["User"])



@router.post("/registration", status_code=status.HTTP_201_CREATED)
async def registration(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter_by(uid=user.uid).first()

    if db_user is None:
        new_user = UserModel(**user.model_dump())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        new_fcm_token_user = FCMTokenModel(
            user_id=new_user.id,
            token=new_user.fcmToken
        )
        db.add(new_fcm_token_user)
        db.commit()
        db.refresh(new_fcm_token_user)
        uid = new_user.uid
        fcm_token = new_fcm_token_user.token

    else:
        db_user.fcmToken = user.fcmToken
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        db_fcm_token_user = db.query(FCMTokenModel).filter_by(user_id=db_user.id).first()
        db_fcm_token_user.token = db_user.fcmToken
        db.add(db_fcm_token_user)
        db.commit()
        db.refresh(db_fcm_token_user)
        uid=db_user.uid
        fcm_token=db_fcm_token_user.token


    token = create_access_token(data={"sub": uid, "fcmToken": fcm_token})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user":db_user

    }


@router.get("/user", response_model=List[UserRead],status_code=status.HTTP_200_OK)
async def get_all_users(db: Session = Depends(get_db)):
    users = db.query(UserModel).all()
    return users


@router.delete("/delete",status_code=status.HTTP_200_OK)
async def delete_user(db: Session = Depends(get_db),user: dict = Depends(get_user_info)):
    user_id=user["id"]
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if db_user is None :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message":"user deleted successfully"}