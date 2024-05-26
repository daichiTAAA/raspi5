from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from api.db import get_db
from api.services.camera_service import CameraService
from api.setup_logger import setup_logger

logger, log_decorator = setup_logger(__name__)

router_v1 = APIRouter(
    prefix="/rtsps",
    tags=["RTSP stream operations"],
    responses={404: {"description": "Not found"}},
)


@router_v1.post("/{camera_id}/start")
def start_rtsp_stream(
    camera_id: str,
    camera_service: CameraService = Depends(),
):
    try:
        camera_service.start_rtsp_stream(camera_id)
        logger.info(f"Stream started for camera {camera_id}")
        return {"message": f"Live stream started for camera {camera_id}"}
    except HTTPException as e:
        if e.status_code == 400 and e.detail == "Camera is already streaming":
            logger.warning(
                f"Warnig error starting stream {camera_id} but ignore it: {e}"
            )
            return {"error": str(e)}
        else:
            logger.error(f"Error starting stream {camera_id}: {e}")
            raise e
    except Exception as e:
        logger.error(f"Error starting stream for camera {camera_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.get("/{camera_id}")
async def get_rtsp_stream(camera_id: str, camera_service: CameraService = Depends()):
    try:
        logger.info(f"Live stream retrieved for camera {camera_id}")
        return StreamingResponse(
            camera_service.get_rtsp_stream(camera_id),
            media_type="multipart/x-mixed-replace;boundary=frame",
        )
    except HTTPException as e:
        logger.error(f"Error retrieving stream for camera {camera_id}: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error retrieving stream for camera {camera_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.post("/{camera_id}/stop")
async def stop_rtsp_stream(camera_id: str, camera_service: CameraService = Depends()):
    try:
        await camera_service.stop_rtsp_stream(camera_id)
        logger.info(f"Stream stopped for camera {camera_id}")
        return {"message": f"Live stream stopped for camera {camera_id}"}
    except HTTPException as e:
        logger.error(f"Error stopping rtsp stream for camera {camera_id}: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error stopping rtsp stream for camera {camera_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
