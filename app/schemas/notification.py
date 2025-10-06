from datetime import datetime
from pydantic import BaseModel,ConfigDict
from typing import Optional

class NotificationBase(BaseModel):
    race_id: int
    notification_hour: int

class NotificationDelete(NotificationBase):
    pass

class NotificationCreate(NotificationBase):
    pass

class NotificationUpdate(BaseModel):
    notification_hour: Optional[int] = None

class NotificationResponse(NotificationBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
