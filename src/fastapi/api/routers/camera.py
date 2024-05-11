from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from api.services.camera_service import CameraService
from api.schemas.camera import CameraAddRequest
from api.setup_logger import setup_logger

logger, log_decorator = setup_logger(__name__)

router_v1 = APIRouter(
    prefix="/cameras",
    tags=["camera stream"],
    responses={404: {"description": "Not found"}},
)


@router_v1.post("")
async def add_camera(
    camera_request: CameraAddRequest, camera_service: CameraService = Depends()
):
    await camera_service.add_camera(camera_request.camera_id, camera_request.rtsp_url)
    return {"message": f"Camera {camera_request.camera_id} added successfully"}


@router_v1.post("/{camera_id}/start")
async def start_stream(
    camera_id: str,
    camera_service: CameraService = Depends(),
):
    try:
        await camera_service.start_stream(camera_id)
        return {"message": f"Stream started for camera {camera_id}"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.get("/{camera_id}/stream")
def get_stream(camera_id: str, camera_service: CameraService = Depends()):
    try:
        stream = camera_service.get_stream(camera_id)
        return StreamingResponse(stream, media_type="application/vnd.apple.mpegurl")
    except HTTPException as e:
        raise e


@router_v1.post("/{camera_id}/stop")
async def stop_stream(camera_id: str, camera_service: CameraService = Depends()):
    try:
        await camera_service.stop_stream(camera_id)
        return {"message": f"Stream stopped for camera {camera_id}"}
    except HTTPException as e:
        raise e


@router_v1.delete("/{camera_id}")
async def remove_camera(camera_id: str, camera_service: CameraService = Depends()):
    try:
        await camera_service.remove_camera(camera_id)
        return {"message": f"Camera {camera_id} removed successfully"}
    except HTTPException as e:
        raise e
