from fastapi import APIRouter, Depends, HTTPException,status,Form
from app.auth.schemas.auth_user import (
    AuthUserCreate,
    AuthUserOTPVerify,
    AuthResendOTP,
    AuthResetPassword,
    AuthGoogleLogin,
    UpdateSubscriptionRequest,
)
from google.oauth2 import id_token
from google.auth.transport import requests
import os
import requests as http_requests
import jwt
import json
from typing import Optional
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
    return {
        "access_token": token,
        "token_type": "bearer",
        "is_subscribed": bool(db_user.is_subscribed) if db_user.is_subscribed is not None else False,
        "email": db_user.email,
        "first_name": db_user.first_name,
    }



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


@router.post("/google/login", status_code=status.HTTP_200_OK)
async def google_login(
    access_token: str = Form(...),
    fcm_token: str = Form(...),
    db: Session = Depends(get_db)
):
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Please provide the access token."
        )
    try:
        response = http_requests.get(
            f'https://www.googleapis.com/oauth2/v2/userinfo?access_token={access_token}'
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Invalid Google token"
            )
        user_info = response.json()
        email = user_info.get("email")
        name = user_info.get("name", "")
        picture = user_info.get("picture", "")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No email address was found from the Google account."
            )
    except http_requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There was a problem connecting to the Google API."
        )
    
    db_user = db.query(AuthUserModel).filter(AuthUserModel.email == email).first()
    if db_user is None:
        new_user = AuthUserModel(
            first_name=name.split(" ")[0] if name else "",
            email=email,
            password=None, 
            is_verified=True,  
            profile_image=picture,
            auth_provider="google",
            role="customer"
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        db_user = new_user
    user_data = UserCreate(**{
        "uid": email,
        "fcmToken": fcm_token,
    })
    token = await registration(user_data, db)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "is_subscribed": bool(db_user.is_subscribed) if db_user.is_subscribed is not None else False,
        "email": db_user.email,
        "first_name": db_user.first_name,
        "message": "Google login successful"
    }


@router.post("/apple/login", status_code=status.HTTP_200_OK)
async def apple_login(
    identity_token: str = Form(...),
    fcm_token: str = Form(...),
    name: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    if not identity_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Please provide the identity token."
        )
    try:
        apple_keys_url = "https://appleid.apple.com/auth/keys"
        key_payload = http_requests.get(apple_keys_url).json()
        unverified_header = jwt.get_unverified_header(identity_token)
        unverified_header = jwt.get_unverified_header(identity_token)
        kid = unverified_header.get('kid')
        if not kid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token header (kid missing)")
        rsa_key = {}
        for key in key_payload['keys']:
            if key['kid'] == kid:
                rsa_key = {
                    'kty': key['kty'],
                    'kid': key['kid'],
                    'use': key['use'],
                    'n': key['n'],
                    'e': key['e']
                }
                break
                
        if not rsa_key:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Apple public key not found")
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(rsa_key))
        decoded_token = jwt.decode(
            identity_token, 
            public_key, 
            algorithms=['RS256'], 
            options={"verify_aud": False}  
        )
        
        email = decoded_token.get("email")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not found in Apple token"
            )
            
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Problem with Apple authentication: {str(e)}")

    db_user = db.query(AuthUserModel).filter(AuthUserModel.email == email).first()
    
    if db_user is None:
        new_user = AuthUserModel(
            first_name=name if name else "Apple User",
            email=email,
            password=None,
            is_verified=True,
            profile_image="",
            auth_provider="apple",
            role="customer"
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        db_user = new_user
    else:
        if name and not db_user.first_name:
            db_user.first_name = name
            db.commit()
            db.refresh(db_user)
    
    user_data = UserCreate(**{
        "uid": email,
        "fcmToken": fcm_token,
    })
    token = await registration(user_data, db)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "is_subscribed": bool(db_user.is_subscribed) if db_user.is_subscribed is not None else False,
        "email": db_user.email,
        "first_name": db_user.first_name,
        "message": "Apple login successful"
    }


@router.post("/update-subscription", status_code=status.HTTP_200_OK)
async def update_subscription(data: UpdateSubscriptionRequest, db: Session = Depends(get_db)):
    db_user = db.query(AuthUserModel).filter(AuthUserModel.email == data.email).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    db_user.is_subscribed = data.is_subscribed
    if data.product_id:
        db_user.subscription_product_id = data.product_id
    if data.purchase_token:
        db_user.subscription_purchase_token = data.purchase_token
    
    db.commit()
    db.refresh(db_user)

    user_record = db.query(UserModel).filter(UserModel.uid == data.email).first()
    if user_record:
        user_record.is_subscribed = data.is_subscribed
        db.commit()

    return {
        "message": "Subscription updated successfully",
        "is_subscribed": db_user.is_subscribed,
        "email": db_user.email
    }


@router.get("/subscription-status/{email}", status_code=status.HTTP_200_OK)
async def get_subscription_status(email: str, db: Session = Depends(get_db)):
    db_user = db.query(AuthUserModel).filter(AuthUserModel.email == email).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {
        "email": db_user.email,
        "is_subscribed": bool(db_user.is_subscribed) if db_user.is_subscribed is not None else False,
        "product_id": db_user.subscription_product_id
    }



