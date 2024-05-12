from pydantic import BaseModel, ConfigDict, ValidationError
from typing import Any
import ffmpeg


class Camera(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: str
    rtsp_url: str
    process: Any | None
    cap: Any | None
