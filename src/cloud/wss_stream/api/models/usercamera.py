from sqlalchemy import Column, String

from api.db import Base


class UserCamera(Base):
    __tablename__ = "usercameras"
    user_id = Column(String, primary_key=True)
    camera_id = Column(String, primary_key=True)
    rtsp_url = Column(String)
