from typing import Any
from pydantic import BaseModel


class CameraInstance(BaseModel):
    camera_id: str
    rtsp_url: str
    hls_process: Any | None
    jpeg_extract_process: Any | None
    jpeg_stream_process: Any | None
    cap: Any | None
    m3u8_file_path: str | None
    jpeg_dir_path: str | None
    hls_last_access_time: float | None
    jpeg_fps: int | None
    jpeg_last_access_time: float | None
    jpeg_stream_last_access_time: float | None
