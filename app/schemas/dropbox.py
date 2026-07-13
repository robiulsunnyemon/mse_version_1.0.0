from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class DropboxBase(BaseModel):
    title: str
    subtitle: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None

class DropboxCreate(DropboxBase):
    pass

class DropboxUpdate(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None

class DropboxResponse(DropboxBase):
    id: int
    image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
