from fastapi import APIRouter, Depends, HTTPException,status
from app.auth.schemas.auth_user import AuthUserCreate, AuthUserOTPVerify, AuthResendOTP, AuthResetPassword
from app.db.db import get_db
from app.auth.model.auth_user import AuthUserModel
from sqlalchemy.orm import Session
from app.models.user import UserModel
from app.utils.get_hashed_password import get_hashed_password,verify_password
from app.utils.email_config import send_otp
from app.utils.otp_generate import generate_otp
from app.schemas.send_otp import SendOtpModel
from app.utils.token_generation import create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from app.routers.user import registration,delete_user
from app.schemas.user import UserCreate, UserRead
from app.utils.user_info import get_user_info

router = APIRouter(prefix="/auth/user", tags=["Auth User"])



@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user:AuthUserCreate,db: Session = Depends(get_db)):
    db_user = db.query(AuthUserModel).filter(AuthUserModel.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="You have already registered")
    hashed_password = get_hashed_password(user.password)
    otp=generate_otp()
    send_otp_data=SendOtpModel(email=user.email,otp=otp)
    await send_otp(send_otp_data)
    new_user = AuthUserModel(
        first_name=user.first_name,
        email=user.email,
        password=hashed_password,
        otp=otp,
        role=user.role,
        is_verified=False,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message":"A 6 digit OTP has delivered. please check your email","email":new_user.email,"otp":new_user.otp}




@router.post("/user_otp_verify", status_code=status.HTTP_200_OK)
async def verify_otp(user:AuthUserOTPVerify,db: Session = Depends(get_db)):
    db_user = db.query(AuthUserModel).filter(AuthUserModel.email == user.email).first()
    if db_user is None :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    if user.otp != db_user.otp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Wrong OTP")
    db_user.is_verified = True
    db.commit()
    db.refresh(db_user)
    return {"message":"You have  verified"}




@router.post("/login", status_code=status.HTTP_200_OK)

async def login(user_data: UserCreate,form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(AuthUserModel).filter(AuthUserModel.email == form_data.username).first()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not verify_password(form_data.password, db_user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong password")

    if not db_user.is_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You are not verified, please check your email")

    token=await registration(user_data,db)
    # token = create_access_token(data={"sub": db_user.email, "role": db_user.role, "user_id": db_user.id})
    return {"access_token": token, "token_type": "bearer"}




@router.post("/login_for_admin", status_code=status.HTTP_200_OK)

async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(AuthUserModel).filter(AuthUserModel.email == form_data.username).first()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not verify_password(form_data.password, db_user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong password")

    if not db_user.is_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You are not verified, please check your email")

    if not db_user.role=="admin":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You are not an admin")

    token = create_access_token(data={"sub": db_user.email, "role": db_user.role, "user_id": db_user.id})
    return {"access_token": token, "token_type": "bearer"}




@router.post("/resend-otp", status_code=status.HTTP_200_OK)
async def resend_otp(user:AuthResendOTP,db: Session = Depends(get_db)):
    db_user = db.query(AuthUserModel).filter(AuthUserModel.email == user.email).first()
    if db_user is None :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    otp=generate_otp()
    send_otp_data = SendOtpModel(email=user.email, otp=otp)
    await send_otp(send_otp_data)
    db_user.otp=otp
    db.commit()
    db.refresh(db_user)
    return {"message":"A 6 digit OTP has delivered. please check your email","email":db_user.email,"otp":db_user.otp}




@router.post("/reset_password", status_code=status.HTTP_200_OK)
async def reset_password(user:AuthResetPassword,db: Session = Depends(get_db)):
    db_user = db.query(AuthUserModel).filter(AuthUserModel.email == user.email).first()
    if db_user is None :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    if not db_user.is_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="You are not verified")
    hashed_password = get_hashed_password(user.new_password)
    db_user.password = hashed_password
    db.commit()
    db.refresh(db_user)
    return {"message":"you have reset password successfully"}




@router.delete("/{id}",status_code=status.HTTP_200_OK)
async def delete_auth_user(id:int,db: Session = Depends(get_db)):
    auth_db_user =await db.query(AuthUserModel).filter(AuthUserModel.id == id).first()
    if auth_db_user is None :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    db_user = db.query(UserModel).filter(UserModel.uid == auth_db_user.email).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    db.delete(auth_db_user)
    db.commit()
    return {"message":"user deleted successfully"}




@router.delete("/me",status_code=status.HTTP_200_OK)
async def delete_auth_user_me(user: dict = Depends(get_user_info),db: Session = Depends(get_db)):
    auth_db_user =await db.query(AuthUserModel).filter(AuthUserModel.id == id).first()
    if auth_db_user is None :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    response=await  delete_user(db,user)
    db.delete(auth_db_user)
    db.commit()
    return response