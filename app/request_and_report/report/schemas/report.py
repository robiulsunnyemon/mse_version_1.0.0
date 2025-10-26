from pydantic import BaseModel,EmailStr
from datetime import datetime


class ReportBase(BaseModel):
    user_email:EmailStr
    report_details:str


class ReportCreate(ReportBase):
    pass


class ReportRead(ReportBase):
    user_name: str
    created_at :datetime
    updated_at :datetime
