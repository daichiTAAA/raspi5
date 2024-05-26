from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from api.db import get_db
from api.services.usercamera_service import UserCameraService
from api.setup_logger import setup_logger
import api.cruds as cruds
from api.get_env import env_info

logger, log_decorator = setup_logger(__name__)

router_v1 = APIRouter(
    prefix="/usercamerainstances",
    tags=["Usercamera instance operations"],
    responses={404: {"description": "Not found"}},
)


@router_v1.post("/{user_id}/{camera_id}")
async def create_usercamera_instance(
    user_id: str,
    camera_id: str,
    usercamera_service: UserCameraService = Depends(),
    db: AsyncSession = Depends(get_db),
):
    result = await cruds.get_usercamera_by_user_and_camera_id(db, user_id, camera_id)
    if result is None:
        logger.error(f"Usercamera user_id:{user_id}, camera_id:{camera_id} not found")
        raise HTTPException(status_code=404, detail="Usercamera not found")
    rtsp_url = result.rtsp_url
    try:
        usercamera_service.create_usercamera_instance(
            user_id, camera_id, rtsp_url, env_info.CLOUD_DOMAIN, env_info.CLOUD_PORT
        )
        logger.info(
            f"Usercamera instance created for user {user_id}, camera {camera_id}"
        )
        return {
            "message": f"Usercamera instance created for user {user_id}, camera {camera_id}"
        }
    except HTTPException as e:
        logger.error(
            f"Error creating usercamera instance for user {user_id}, camera {camera_id}: {e}"
        )
        raise e
    except Exception as e:
        logger.error(
            f"Error creating usercamera instance for user {user_id}, camera {camera_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.get("")
def get_usercamera_instances(usercamera_service: UserCameraService = Depends()):
    try:
        usercamera_instances = usercamera_service.get_usercamera_instances()
        logger.info(f"Usercamera instances retrieved")
        return usercamera_instances
    except HTTPException as e:
        logger.error(f"Error retrieving usercamera instances: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error retrieving usercamera instances: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.get("/{user_id}/{camera_id}")
def get_usercamera_instance_by_user_and_camera_id(
    user_id: str, camera_id: str, usercamera_service: UserCameraService = Depends()
):
    try:
        usercamera_instance = (
            usercamera_service.get_usercamera_instance_by_user_and_camera_id(
                user_id, camera_id
            )
        )
        logger.info(
            f"Usercamera instance retrieved for user {user_id}, camera {camera_id}"
        )
        return usercamera_instance
    except HTTPException as e:
        logger.error(
            f"Error retrieving usercamera instance for user {user_id}, camera {camera_id}: {e}"
        )
        raise e
    except Exception as e:
        logger.error(
            f"Error retrieving usercamera instance for user {user_id}, camera {camera_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.delete("/{user_id}/{camera_id}")
def delete_usercamera_instance(
    user_id: str, camera_id: str, usercamera_service: UserCameraService = Depends()
):
    try:
        usercamera_service.delete_usercamera_instance(user_id)
        logger.info(
            f"Usercamera instance deleted for user {user_id}, camera {camera_id}"
        )
        return {
            "message": f"Usercamera instance deleted for user {user_id}, camera {camera_id}"
        }
    except HTTPException as e:
        logger.error(
            f"Error deleting usercamera instance for user {user_id}, camera {camera_id}: {e}"
        )
        raise e
    except Exception as e:
        logger.error(
            f"Error deleting usercamera instance for user {user_id}, camera {camera_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=str(e))
