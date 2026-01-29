from pydantic import BaseModel,EmailStr
from typing import Optional

class AuthUserBase(BaseModel):
    first_name: str
    email: EmailStr
    role: Optional[str]


class AuthUserCreate(AuthUserBase):
    password: str


class AuthUserRead(AuthUserBase):
    id: int


class AuthResendOTP(BaseModel):
    email: EmailStr


class AuthResetPassword(BaseModel):
    email: EmailStr
    new_password: str


class AuthUserOTPVerify(BaseModel):
    email: EmailStr
    otp:str




class AuthUserUpdate(BaseModel):
    first_name: Optional[str]

class AuthGoogleLogin(BaseModel):
    access_token: str
    fcm_token: str
