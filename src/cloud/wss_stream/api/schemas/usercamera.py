from pydantic import BaseModel


class UserCameraCreate(BaseModel):
    user_id: str
    camera_id: str
    rtsp_url: str
