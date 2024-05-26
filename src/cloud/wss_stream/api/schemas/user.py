from pydantic import BaseModel


class UserCreate(BaseModel):
    user_id: str
    camera_id: str
