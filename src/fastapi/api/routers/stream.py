from fastapi import APIRouter, Depends, HTTPException, status, Response
import cv2
import ffmpeg
from typing import List

import api.cruds as cruds
import api.schemas as schemas
from api.setup_logger import setup_logger

logger, log_decorator = setup_logger(__name__)

router_v1 = APIRouter(
    prefix="/stream",
    tags=["stream"],
    responses={404: {"description": "Not found"}},
)

@router_v1.post("/get_frame", response_model=schemas.StreamFrame, response_model_exclude_unset=True)
async def get_frame(stream_get: schemas.StreamGet):
    logger.info(f"routers.get_frame: {stream_get}")
    # FFmpegを使用してRTSPストリームを開く
    rtsp_url = stream_get.rtsp_url
    logger.info(f"routers.get_frame: rtsp_url: {rtsp_url}")
    stream = ffmpeg.input(rtsp_url)
    
    # RTSPストリームからフレームを取得
    encoded_frame = await cruds.get_frame(stream)

    response_frame = schemas.StreamFrame(rtsp_url=rtsp_url, frame=encoded_frame.tobytes())     

    # レスポンスとしてJPEGフレームを返す
    return response_frame