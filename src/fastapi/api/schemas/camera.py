from pydantic import BaseModel


class CameraAddRequest(BaseModel):
    camera_id: str
    rtsp_url: str
