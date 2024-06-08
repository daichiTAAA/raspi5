from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api.db import get_db
from api.services.camera_service import CameraService
from api.setup_logger import setup_logger
import api.schemas as schemas

logger, log_decorator = setup_logger(__name__)

router_v1 = APIRouter(
    prefix="/jpegs",
    tags=["JPEG operations"],
    responses={404: {"description": "Not found"}},
)

time_out: int = 60


@router_v1.post("/{camera_id}/start")
def start_jpeg_extract_process(
    camera_id: str,
    camera_service: CameraService = Depends(),
):
    try:
        logger.info(f"Starting JPEG process for camera {camera_id}")
        camera_service.start_jpeg_extract_process(camera_id, time_out)
        logger.info(f"JPEG process started for camera {camera_id}")
        return {"message": f"JPEG process started for camera {camera_id}"}
    except HTTPException as e:
        if e.status_code == 400 and e.detail == "Camera is already extracting jpeg":
            logger.warning(
                f"Warning error starting JPEG process {camera_id} but ignore it: {e}"
            )
            return {"error": str(e)}
        else:
            logger.error(f"Error starting JPEG process {camera_id}: {e}")
            raise e
    except Exception as e:
        logger.error(f"Error starting JPEG process for camera {camera_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.post("/{camera_id}/keepalive")
def keep_jpeg_extract_process(
    camera_id: str,
    camera_service: CameraService = Depends(),
):
    try:
        camera_service.keep_jpeg_extract_process(camera_id)
        logger.info(f"JPEG process kept for camera {camera_id}")
        return {"message": f"JPEG process kept for camera {camera_id}"}
    except HTTPException as e:
        logger.error(f"Error keeping JPEG process for camera {camera_id}: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error keeping JPEG process for camera {camera_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.post("/{camera_id}/stop")
def stop_jpeg_extract_process(
    camera_id: str, camera_service: CameraService = Depends()
):
    try:
        camera_service.stop_jpeg_extract_process(camera_id)
        logger.info(f"JPEG process stopped for camera {camera_id}")
        return {"message": f"JPEG process stopped for camera {camera_id}"}
    except HTTPException as e:
        logger.error(f"Error stopping JPEG process for camera {camera_id}: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error stopping JPEG process for camera {camera_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.get("/{camera_id}/stream")
def generate_video_stream_from_jpeg(
    camera_id: str, camera_service: CameraService = Depends()
):
    try:
        logger.info(f"Generating video stream from JPEG for camera {camera_id}")
        return camera_service.generate_video_stream_from_jpeg(camera_id, time_out)
    except HTTPException as e:
        logger.error(
            f"Error generating video stream from JPEG for camera {camera_id}: {e}"
        )
        raise e
    except Exception as e:
        logger.error(
            f"Error generating video stream from JPEG for camera {camera_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.get("/{camera_id}/latest_jpeg")
def get_latest_jpeg(camera_id: str, camera_service: CameraService = Depends()):
    try:
        logger.info(f"Getting latest JPEG for camera {camera_id}")
        return camera_service.get_latest_jpeg(camera_id)
    except HTTPException as e:
        logger.error(
            f"Error generating video stream from JPEG for camera {camera_id}: {e}"
        )
        raise e
    except Exception as e:
        logger.error(
            f"Error generating video stream from JPEG for camera {camera_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.post("/{camera_id}/stop_stream")
def stop_jpeg_stream_process(camera_id: str, camera_service: CameraService = Depends()):
    try:
        camera_service.stop_jpeg_stream_process(camera_id)
        logger.info(f"JPEG stream process stopped for camera {camera_id}")
        return {"message": f"JPEG stream process stopped for camera {camera_id}"}
    except HTTPException as e:
        logger.error(f"Error stopping JPEG stream process for camera {camera_id}: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error stopping JPEG stream process for camera {camera_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.post("/{camera_id}/keep_stream")
def keep_jpeg_stream_process(camera_id: str, camera_service: CameraService = Depends()):
    try:
        logger.info(f"Keeping JPEG stream process for camera {camera_id}")
        camera_service.keep_jpeg_stream_process(camera_id)
        logger.info(f"JPEG stream process kept for camera {camera_id}")
        return {"message": f"JPEG stream process kept for camera {camera_id}"}
    except HTTPException as e:
        logger.error(f"Error keeping JPEG stream process for camera {camera_id}: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error keeping JPEG stream process for camera {camera_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.delete("/{camera_id}/delete")
def remove_jpeg_files(camera_id: str, camera_service: CameraService = Depends()):
    try:
        camera_service.remove_jpeg_files(camera_id)
        logger.info(f"JPEG directory deleted for camera {camera_id}")
        return {"message": f"JPEG directory deleted for camera {camera_id}"}
    except HTTPException as e:
        logger.error(f"Error deleting JPEG directory for camera {camera_id}: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error deleting JPEG directory for camera {camera_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.post("/{camera_id}/save_area")
async def save_area(
    camera_id: str,
    saving_area: schemas.SaveArea,
    db: AsyncSession = Depends(get_db),
    camera_service: CameraService = Depends(),
):
    try:
        message = await camera_service.save_selected_area(db, camera_id, saving_area)
        logger.info(message)
        return message
    except HTTPException as e:
        logger.error(f"Error saving area for camera {camera_id}: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error saving area for camera {camera_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
