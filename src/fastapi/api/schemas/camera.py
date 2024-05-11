from pydantic import BaseModel


class StreamRequest(BaseModel):
    rtsp_url: str


class StreamResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    detail: str
