from fastapi import APIRouter, Depends, HTTPException

from api.services.camera_service import CameraService
from api.setup_logger import setup_logger

logger, log_decorator = setup_logger(__name__)

router_v1 = APIRouter(
    prefix="/hlss",
    tags=["HLS stream operations"],
    responses={404: {"description": "Not found"}},
)

time_out: int = 60


@router_v1.post("/{camera_id}/start")
def start_hls_stream(
    camera_id: str,
    camera_service: CameraService = Depends(),
):
    try:
        logger.info(f"Starting stream for camera {camera_id}")
        camera_service.start_hls_stream(camera_id, time_out)
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


@router_v1.get("/{camera_id}/url")
def get_hls_stream_url(camera_id: str, camera_service: CameraService = Depends()):
    try:
        hls_stream_url = camera_service.get_hls_stream_url(camera_id)
        logger.info(f"Hls stream url retrieved for camera {camera_id}")
        return hls_stream_url
    except HTTPException as e:
        logger.error(f"Error retrieving hls stream url for camera {camera_id}: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error retrieving hls stream url for camera {camera_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.post("/{camera_id}/keepalive")
def keep_hls_stream(
    camera_id: str,
    camera_service: CameraService = Depends(),
):
    try:
        camera_service.keep_hls_stream(camera_id)
        logger.info(f"Stream kept for camera {camera_id}")
        return {"message": f"Stream kept for camera {camera_id}"}
    except HTTPException as e:
        logger.error(f"Error keeping stream for camera {camera_id}: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error keeping stream for camera {camera_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.post("/{camera_id}/stop")
async def stop_hls_stream(camera_id: str, camera_service: CameraService = Depends()):
    try:
        await camera_service.stop_hls_stream(camera_id)
        logger.info(f"Stream stopped for camera {camera_id}")
        return {"message": f"Stream stopped for camera {camera_id}"}
    except HTTPException as e:
        logger.error(f"Error stopping stream for camera {camera_id}: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error stopping stream for camera {camera_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.get("/{camera_id}/files")
def get_hls_files(camera_id: str, camera_service: CameraService = Depends()):
    try:
        hls_files = camera_service.get_hls_files(camera_id)
        logger.info(f"Hls files retrieved for camera {camera_id}")
        return hls_files
    except HTTPException as e:
        logger.error(f"Error retrieving hls files for camera {camera_id}: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error retrieving hls files for camera {camera_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.delete("/{camera_id}/files")
def remove_hls_files(camera_id: str, camera_service: CameraService = Depends()):
    try:
        camera_service.remove_hls_files(camera_id)
        logger.info(f"Hls files removed for camera {camera_id}")
        return {"message": f"Hls files removed for camera {camera_id}"}
    except HTTPException as e:
        logger.error(f"Error removing hls files for camera {camera_id}: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error removing hls files for camera {camera_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
