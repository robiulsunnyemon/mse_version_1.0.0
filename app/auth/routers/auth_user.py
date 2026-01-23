from fastapi import APIRouter, Depends, HTTPException,status,Form
from app.auth.schemas.auth_user import AuthUserCreate, AuthUserOTPVerify, AuthResendOTP, AuthResetPassword, AuthGoogleLogin
from google.oauth2 import id_token
from google.auth.transport import requests
import os
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
from app.routers.user import registration
from app.schemas.user import UserCreate

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

async def login(
        email: str = Form(...),
        password: str = Form(...),
        fcm_token: str = Form(...),
        db: Session = Depends(get_db)
):
    db_user = db.query(AuthUserModel).filter(AuthUserModel.email == email).first()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Your Email is wrong")

    if not verify_password(password, db_user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong password")

    if not db_user.is_verified:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not verified, please check your email")

    user_data=UserCreate(**{
        "uid": email,
        "fcmToken": fcm_token,
    })
    token=await registration(user_data,db)
    return {"access_token": token, "token_type": "bearer"}



@router.post("/login_for_admin", status_code=status.HTTP_200_OK)

async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(AuthUserModel).filter(AuthUserModel.email == form_data.username).first()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not verify_password(form_data.password, db_user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong password")

    if not db_user.is_verified:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You are not verified, please check your email")

    if not db_user.role=="admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not an admin")

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






@router.delete("/{email}", status_code=status.HTTP_200_OK)
async def delete_auth_user_me(email: str, db: Session = Depends(get_db)):
    auth_db_user = db.query(AuthUserModel).filter(AuthUserModel.email == email).first()
    if not auth_db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_user = db.query(UserModel).filter(UserModel.uid == email).first()
    if db_user:
        db.delete(db_user)

    db.delete(auth_db_user)
    db.commit()

    return {"message": "User deleted successfully"}


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_auth_user(db: Session = Depends(get_db)):
    auth_db_user = db.query(AuthUserModel).all()
    return {"auth_db_user": auth_db_user}


@router.post("/google-login", status_code=status.HTTP_200_OK)
async def google_login(data: AuthGoogleLogin, db: Session = Depends(get_db)):
    try:
        # Verify ID token
        id_info = id_token.verify_oauth2_token(data.id_token, requests.Request(), os.getenv("GOOGLE_CLIENT_ID"))

        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid issuer")

        email = id_info['email']
        first_name = id_info.get('given_name', id_info.get('name', ''))
        profile_image = id_info.get('picture')

        # Check if user exists in AuthUserModel
        db_user = db.query(AuthUserModel).filter(AuthUserModel.email == email).first()

        if not db_user:
            # Create new auth user
            db_user = AuthUserModel(
                first_name=first_name,
                email=email,
                is_verified=True,
                auth_provider="google",
                profile_image=profile_image,
                role="customer"
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
        else:
            # Update existing user if needed
            db_user.auth_provider = "google"
            if profile_image:
                db_user.profile_image = profile_image
            db_user.is_verified = True
            db.commit()
            db.refresh(db_user)

        # Call registration to ensure UserModel and FCM token are sync'd
        user_create_data = UserCreate(
            uid=email,
            fcmToken=data.fcm_token
        )
        token_data = await registration(user_create_data, db)
        
        return token_data

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid Google token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Google login failed: {str(e)}")