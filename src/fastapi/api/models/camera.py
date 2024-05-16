from pydantic import BaseModel, ConfigDict, ValidationError
from typing import Any


class Camera(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: str
    rtsp_url: str
    process: Any | None
    cap: Any | None
    m3u8_file_path: str | None
    last_access_time: float | None
