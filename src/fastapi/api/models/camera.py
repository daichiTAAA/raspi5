from pydantic import BaseModel
import ffmpeg


class Camera(BaseModel):
    id: str
    process: ffmpeg.nodes.OutputStream
