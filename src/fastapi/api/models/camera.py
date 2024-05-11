from pydantic import BaseModel, ConfigDict, ValidationError
import ffmpeg


class Camera(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: str
    process: ffmpeg.nodes.OutputStream
