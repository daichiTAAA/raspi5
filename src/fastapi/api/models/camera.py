from typing import Any

from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

from api.db import Base


class Camera(Base):
    __tablename__ = "cameras"
    camera_id = Column(String, primary_key=True)
    rtsp_url = Column(String)


class CameraInUse(BaseModel):
    camera_id: str
    rtsp_url: str
    process: Any | None
    cap: Any | None
    m3u8_file_path: str | None
    last_access_time: float | None
