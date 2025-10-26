from pydantic import BaseModel,EmailStr



class RequestBase(BaseModel):
    user_email:EmailStr
    request_details:str


class RequestCreate(RequestBase):
    pass


class RequestRead(RequestBase):
    user_name:str
    created_at :str
    updated_at :str
