from datetime import datetime
from pydantic import BaseModel,ConfigDict
from typing import Optional

class PromotionBase(BaseModel):
    title: str
    description: str

class PromotionCreate(PromotionBase):
    pass

class PromotionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class PromotionResponse(PromotionBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
