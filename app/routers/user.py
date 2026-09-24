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

    # Check if incoming token is a valid string
    incoming_token = user.fcmToken.strip() if user.fcmToken else ""
    is_valid_token = bool(incoming_token and incoming_token.lower() not in ["null", "none", "undefined", ""])

    if db_user is None:
        user_dict = user.model_dump()
        user_dict["fcmToken"] = incoming_token if is_valid_token else None
        new_user = UserModel(**user_dict)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        if is_valid_token:
            new_fcm_token_user = FCMTokenModel(
                user_id=new_user.id,
                token=incoming_token
            )
            db.add(new_fcm_token_user)
            db.commit()
            db.refresh(new_fcm_token_user)
            fcm_token = new_fcm_token_user.token
        else:
            fcm_token = None
        uid = new_user.uid
        db_user = new_user

    else:
        if is_valid_token:
            db_user.fcmToken = incoming_token
            db.add(db_user)
            db.commit()
            db.refresh(db_user)

            db_fcm_token_user = db.query(FCMTokenModel).filter_by(user_id=db_user.id).first()
            if db_fcm_token_user:
                db_fcm_token_user.token = incoming_token
                db.add(db_fcm_token_user)
            else:
                db_fcm_token_user = FCMTokenModel(
                    user_id=db_user.id,
                    token=incoming_token
                )
                db.add(db_fcm_token_user)
            db.commit()
            db.refresh(db_fcm_token_user)
            fcm_token = db_fcm_token_user.token
        else:
            # Preserve existing token if incoming token is null/invalid
            db_fcm_token_user = db.query(FCMTokenModel).filter_by(user_id=db_user.id).first()
            fcm_token = db_fcm_token_user.token if db_fcm_token_user else db_user.fcmToken

        uid = db_user.uid

    token = create_access_token(data={"sub": uid, "fcmToken": fcm_token})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": db_user
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