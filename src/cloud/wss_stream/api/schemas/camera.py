from pydantic import BaseModel


class CameraCreate(BaseModel):
    camera_id: str
    rtsp_url: str
