from pydantic import BaseModel,EmailStr



class RequestBase(BaseModel):
    user_name:str
    user_email:EmailStr
    report_details:str


class RequestCreate(RequestBase):
    pass


class RequestRead(RequestBase):
    created_at :str
    updated_at :str
