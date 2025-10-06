from pydantic import BaseModel,EmailStr

class SendOtpModel(BaseModel):
    email: EmailStr
    otp: int