from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from api.db import get_db
from api.setup_logger import setup_logger
import api.schemas as schemas
import api.cruds as cruds

logger, log_decorator = setup_logger(__name__)

router_v1 = APIRouter(
    prefix="/cameras",
    tags=["Camera DB operations"],
    responses={404: {"description": "Not found"}},
)


@router_v1.post("")
async def create_camera(
    camera: schemas.CameraCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await cruds.get_camera_by_camera_id(db, camera.camera_id)
        if result is not None:
            logger.error(f"Camera {camera.camera_id} already registered")
            raise HTTPException(status_code=400, detail="Camera already registered")
        created_camera = await cruds.create_camera(db, camera)
        logger.info(f"Created Camera: {created_camera}")
        return created_camera
    except HTTPException as e:
        if e.status_code == 400 and e.detail == "Camera already registered":
            logger.warning(
                f"Warnig error adding camera {camera.camera_id} but ignore it: {e}"
            )
            return {"error": str(e)}
        else:
            logger.error(f"Error adding camera {camera.camera_id}: {e}")
            raise e
    except Exception as e:
        logger.error(f"Error adding camera {camera.camera_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.get("")
async def get_cameras(db: AsyncSession = Depends(get_db)):
    try:
        cameras = await cruds.get_cameras(db)
        logger.info(f"Cameras retrieved successfully")
        return cameras
    except HTTPException as e:
        logger.error(f"Error retrieving cameras: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error retrieving cameras: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.get("/{camera_id}")
async def get_camera_by_camera_id(camera_id: str, db: AsyncSession = Depends(get_db)):
    try:
        camera = await cruds.get_camera_by_camera_id(db, camera_id)
        if camera is None:
            logger.error(f"Camera {camera_id} not found")
            raise HTTPException(status_code=404, detail="Camera not found")
        logger.info(f"Camera {camera_id} retrieved successfully")
        return camera
    except HTTPException as e:
        logger.error(f"Error retrieving camera {camera_id}: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error retrieving camera {camera_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.put("/{camera_id}")
async def update_camera(
    camera_id: str,
    camera: schemas.CameraUpdate,
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await cruds.get_camera_by_camera_id(db, camera_id)
        if result is None:
            logger.error(f"Camera {camera_id} not found")
            raise HTTPException(status_code=404, detail="Camera not found")
        updated_camera = await cruds.update_camera(db, camera_id, camera)
        if updated_camera is None:
            logger.error(f"Error updating camera {camera_id}")
            raise HTTPException(status_code=500, detail="Error updating camera")
        logger.info(f"Updated Camera: {updated_camera}")
        return updated_camera
    except HTTPException as e:
        if (
            e.status_code == 409
            and e.detail == f"Camera with new camera_id already exists"
        ):
            logger.warning(f"Conflict error updating camera {camera_id}: {e}")
            raise HTTPException(
                status_code=409,
                detail=f"Camera with new camera_id already exists",
            )
        logger.error(f"Error updating camera {camera_id}: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error updating camera {camera_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.delete("/{camera_id}")
async def delete_camera(
    camera_id: str,
    db: AsyncSession = Depends(get_db),
):
    try:
        camera = await cruds.get_camera_by_camera_id(db, camera_id)
        if camera is None:
            logger.error(f"Camera {camera_id} not found")
            raise HTTPException(status_code=404, detail="Camera not found")
        await cruds.delete_camera(db, camera_id)
        logger.info(f"Camera {camera_id} deleted successfully")
        return {"message": f"Camera {camera_id} deleted successfully"}
    except HTTPException as e:
        logger.error(f"Error deleting camera {camera_id}: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error deleting camera {camera_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
