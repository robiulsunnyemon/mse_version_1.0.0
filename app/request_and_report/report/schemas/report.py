from pydantic import BaseModel,EmailStr



class ReportBase(BaseModel):
    user_email:EmailStr
    report_details:str


class ReportCreate(ReportBase):
    pass


class ReportRead(ReportBase):
    user_name: str
    created_at :str
    updated_at :str
