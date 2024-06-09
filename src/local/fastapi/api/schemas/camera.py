from pydantic import BaseModel


class CameraCreate(BaseModel):
    camera_id: str
    rtsp_url: str


class CameraUpdate(BaseModel):
    camera_id: str
    rtsp_url: str
    area_selected_jpeg_path: str
    area_selected_jpeg_width: str
    area_selected_jpeg_height: str
    selected_area_start_x: str
    selected_area_start_y: str
    selected_area_end_x: str
    selected_area_end_y: str


class SaveArea(BaseModel):
    area_selected_jpeg_data: bytes
    area_selected_jpeg_width: str
    area_selected_jpeg_height: str
    selected_area_start_x: str
    selected_area_start_y: str
    selected_area_end_x: str
    selected_area_end_y: str


class GetArea(BaseModel):
    area_selected_jpeg_data: bytes
    area_selected_jpeg_width: str
    area_selected_jpeg_height: str
    selected_area_start_x: str
    selected_area_start_y: str
    selected_area_end_x: str
    selected_area_end_y: str
