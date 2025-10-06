from  pydantic import BaseModel
from datetime import datetime

class NotificationBox(BaseModel):
    user_id :int
    notification_title: str
    notification_body: str
    created_at:datetime