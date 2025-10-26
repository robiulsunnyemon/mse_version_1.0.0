from pydantic import BaseModel,EmailStr
from datetime import datetime


class RequestBase(BaseModel):
    user_email:EmailStr
    request_details:str


class RequestCreate(RequestBase):
    pass


class RequestRead(RequestBase):
    user_name:str
    created_at :datetime
    updated_at :datetime
