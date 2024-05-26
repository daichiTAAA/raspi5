from typing import Any
from pydantic import BaseModel


class UserInstance(BaseModel):
    user_id: str
    camera_id: str
    rtsp_url: str
    wss_url: str
    wss_process: Any | None
    wss_stream_last_access_time: float | None
