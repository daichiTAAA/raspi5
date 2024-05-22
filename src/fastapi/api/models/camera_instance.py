from typing import Any
from pydantic import BaseModel


class CameraInstance(BaseModel):
    camera_id: str
    rtsp_url: str
    hls_process: Any | None
    cap: Any | None
    m3u8_file_path: str | None
    last_access_time: float | None
