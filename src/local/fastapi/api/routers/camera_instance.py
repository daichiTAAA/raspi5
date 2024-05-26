from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from api.db import get_db
from api.services.camera_service import CameraService
from api.setup_logger import setup_logger
import api.cruds as cruds

logger, log_decorator = setup_logger(__name__)

router_v1 = APIRouter(
    prefix="/camerainstances",
    tags=["Camera instance operations"],
    responses={404: {"description": "Not found"}},
)


@router_v1.post("/{camera_id}")
async def create_camera_instance(
    camera_id: str,
    camera_service: CameraService = Depends(),
    db: AsyncSession = Depends(get_db),
):
    result = await cruds.get_camera_by_camera_id(db, camera_id)
    if result is None:
        logger.error(f"Camera {camera_id} not found")
        raise HTTPException(status_code=404, detail="Camera not found")
    rtsp_url = result.rtsp_url
    try:
        camera_service.create_camera_instance(camera_id, rtsp_url)
        logger.info(f"Camera instance created for camera {camera_id}")
        return {"message": f"Camera instance created for camera {camera_id}"}
    except HTTPException as e:
        logger.error(f"Error creating camera instance for camera {camera_id}: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error creating camera instance for camera {camera_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.get("")
def get_camera_instances(camera_service: CameraService = Depends()):
    try:
        camera_instances = camera_service.get_camera_instances()
        logger.info(f"Camera instances retrieved")
        return camera_instances
    except HTTPException as e:
        logger.error(f"Error retrieving camera instances: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error retrieving camera instances: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.get("/{camera_id}")
def get_camera_instance_by_camera_id(
    camera_id: str, camera_service: CameraService = Depends()
):
    try:
        camera_instance = camera_service.get_camera_instance_by_camera_id(camera_id)
        logger.info(f"Camera instance retrieved for camera {camera_id}")
        return camera_instance
    except HTTPException as e:
        logger.error(f"Error retrieving camera instance for camera {camera_id}: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error retrieving camera instance for camera {camera_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.delete("/{camera_id}")
def delete_camera_instance(camera_id: str, camera_service: CameraService = Depends()):
    try:
        camera_service.delete_camera_instance(camera_id)
        logger.info(f"Camera instance deleted for camera {camera_id}")
        return {"message": f"Camera instance deleted for camera {camera_id}"}
    except HTTPException as e:
        logger.error(f"Error deleting camera instance for camera {camera_id}: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error deleting camera instance for camera {camera_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
