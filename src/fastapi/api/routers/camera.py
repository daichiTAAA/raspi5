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
    try:
        await camera_service.add_camera(
            camera_request.camera_id, camera_request.rtsp_url
        )
        logger.info(f"Camera {camera_request.camera_id} added successfully")
        return {"message": f"Camera {camera_request.camera_id} added successfully"}
    except HTTPException as e:
        if e.status_code == 400 and e.detail == "Camera already exists":
            logger.warning(
                f"Warnig error adding camera {camera_request.camera_id} but ignore it: {e}"
            )
            return {"error": str(e)}
        else:
            logger.error(f"Error adding camera {camera_request.camera_id}: {e}")
            raise e
    except Exception as e:
        logger.error(f"Error adding camera {camera_request.camera_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.post("/{camera_id}/start")
def start_stream(
    camera_id: str,
    camera_service: CameraService = Depends(),
):
    try:
        camera_service.start_stream(camera_id)
        logger.info(f"Stream started for camera {camera_id}")
        return {"message": f"Stream started for camera {camera_id}"}
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


@router_v1.get("/{camera_id}/stream")
def get_stream(camera_id: str, camera_service: CameraService = Depends()):
    try:
        stream = camera_service.get_stream(camera_id)
        logger.info(f"Stream retrieved for camera {camera_id}")
        return stream
    except HTTPException as e:
        logger.error(f"Error retrieving stream for camera {camera_id}: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error retrieving stream for camera {camera_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.post("/{camera_id}/stop")
async def stop_stream(camera_id: str, camera_service: CameraService = Depends()):
    try:
        await camera_service.stop_stream(camera_id)
        logger.info(f"Stream stopped for camera {camera_id}")
        return {"message": f"Stream stopped for camera {camera_id}"}
    except HTTPException as e:
        logger.error(f"Error stopping stream for camera {camera_id}: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error stopping stream for camera {camera_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.delete("/{camera_id}")
async def remove_camera(camera_id: str, camera_service: CameraService = Depends()):
    try:
        await camera_service.remove_camera(camera_id)
        logger.info(f"Camera {camera_id} removed successfully")
        return {"message": f"Camera {camera_id} removed successfully"}
    except HTTPException as e:
        logger.error(f"Error removing camera {camera_id}: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error removing camera {camera_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.post("/{camera_id}/livestart")
def start_live_stream(
    camera_id: str,
    camera_service: CameraService = Depends(),
):
    try:
        camera_service.start_live_stream(camera_id)
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


@router_v1.get("/{camera_id}/live")
async def get_live_stream(camera_id: str, camera_service: CameraService = Depends()):
    try:
        logger.info(f"Live stream retrieved for camera {camera_id}")
        return StreamingResponse(
            camera_service.get_live_stream(camera_id),
            media_type="multipart/x-mixed-replace;boundary=frame",
        )
    except HTTPException as e:
        logger.error(f"Error retrieving stream for camera {camera_id}: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error retrieving stream for camera {camera_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.post("/{camera_id}/livestop")
async def stop_live_stream(camera_id: str, camera_service: CameraService = Depends()):
    try:
        await camera_service.stop_live_stream(camera_id)
        logger.info(f"Stream stopped for camera {camera_id}")
        return {"message": f"Live stream stopped for camera {camera_id}"}
    except HTTPException as e:
        logger.error(f"Error stopping live stream for camera {camera_id}: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error stopping live stream for camera {camera_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
