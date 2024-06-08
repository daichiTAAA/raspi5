from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

from api.db import Base


class Camera(Base):
    __tablename__ = "cameras"
    camera_id = Column(String, primary_key=True)
    rtsp_url = Column(String)
    area_selected_jpeg_path = Column(String)
    area_selected_jpeg_width = Column(String)
    area_selected_jpeg_height = Column(String)
    selected_area_start_x = Column(String)
    selected_area_start_y = Column(String)
    selected_area_end_x = Column(String)
    selected_area_end_y = Column(String)
