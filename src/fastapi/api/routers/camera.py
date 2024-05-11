from fastapi import APIRouter, Depends, Response, HTTPException
import cv2
import ffmpeg
from typing import List

from api.schemas.camera import StreamRequest, StreamResponse, ErrorResponse
from api.services.camera_service import CameraService
from api.setup_logger import setup_logger

logger, log_decorator = setup_logger(__name__)

router_v1 = APIRouter(
    prefix="/camera_stream",
    tags=["camera stream"],
    responses={404: {"description": "Not found"}},
)


@router_v1.post(
    "/start_stream/{camera_id}",
    response_model=StreamResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def start_stream(
    camera_id: str,
    stream_request: StreamRequest,
    camera_service: CameraService = Depends(),
):
    try:
        await camera_service.start_stream(camera_id, stream_request.rtsp_url)
        return {"message": f"Stream started for camera {camera_id}"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.get("/get_frame/{camera_id}", responses={404: {"model": ErrorResponse}})
async def get_frame(camera_id: str, camera_service: CameraService = Depends()):
    frame = await camera_service.get_frame(camera_id)
    if frame:
        return Response(content=frame, media_type="image/jpeg")
    else:
        raise HTTPException(
            status_code=404, detail=f"No frame available for camera {camera_id}"
        )


@router_v1.post("/stop_stream/{camera_id}", response_model=StreamResponse)
async def stop_stream(camera_id: str, camera_service: CameraService = Depends()):
    await camera_service.stop_stream(camera_id)
    return {"message": f"Stream stopped for camera {camera_id}"}
