from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel
import ffmpeg


class StreamBase(BaseModel):
    rtsp_url: str

class StreamGet(StreamBase):
    pass

class StreamFrame(StreamBase):
    frame: bytes