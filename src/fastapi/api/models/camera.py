from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

from api.db import Base


class Camera(Base):
    __tablename__ = "cameras"
    camera_id = Column(String, primary_key=True)
    rtsp_url = Column(String)
