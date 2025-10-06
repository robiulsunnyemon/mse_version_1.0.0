from pydantic import BaseModel


class UserBase(BaseModel):
    uid: str
    fcmToken: str


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    uid: str
    fcmToken: str
    id: int

