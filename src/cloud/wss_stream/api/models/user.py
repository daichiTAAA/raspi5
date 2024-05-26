from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

from api.db import Base


class User(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True)
    camera_id = Column(String)
