from typing import Any
from pydantic import BaseModel


class UserInstance(BaseModel):
    user_id: str
    camera_id: str
