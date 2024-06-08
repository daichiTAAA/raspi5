from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import api.models as models
import api.schemas as schemas
from api.setup_logger import setup_logger

logger, log_decorator = setup_logger(__name__)


async def get_cameras(db: AsyncSession):
    logger.info("Fetching all cameras")
    try:
        result = await db.execute(select(models.Camera))
        logger.info("Successfully fetched all cameras")
        return result.scalars().all()
    except Exception as e:
        logger.error(f"Error fetching all cameras: {e}")
        return None


async def get_camera_by_camera_id(db: AsyncSession, camera_id: str):
    """カメラをcamera_idで取得"""
    logger.info(f"Fetching camera with camera_id {camera_id}")
    try:
        result = await db.execute(
            select(models.Camera).filter(models.Camera.camera_id == camera_id)
        )
        logger.info(f"Successfully fetched camera with camera_id {camera_id}")
        return result.scalars().first()
    except Exception as e:
        logger.error(f"Error fetching camera with camera_id {camera_id}: {e}")
        return None


async def create_camera(
    db: AsyncSession, camera: schemas.CameraCreate
) -> models.Camera | None:
    logger.info(f"Creating camera with camera_id {camera.camera_id}")
    try:
        new_camera = models.Camera(
            camera_id=camera.camera_id,
            rtsp_url=camera.rtsp_url,
        )
        db.add(new_camera)
        await db.commit()
        created_camera: models.Camera = models.Camera(
            camera_id=camera.camera_id, rtsp_url=camera.rtsp_url
        )
        logger.info(f"Camera with camera_id {camera.camera_id} created successfully")
        return created_camera
    except Exception as e:
        logger.error(f"Error creating camera with camera_id {camera.camera_id}: {e}")
        await db.rollback()
        return None


async def update_camera(
    db: AsyncSession, camera_id: str, camera: schemas.CameraUpdate
) -> models.Camera | None:
    logger.info(f"Updating camera with camera_id {camera_id}")
    try:
        result = await db.execute(
            select(models.Camera).filter(models.Camera.camera_id == camera_id)
        )
        existing_camera = result.scalars().first()
        if existing_camera is None:
            return None

        # Check if the new camera_id already exists
        if camera_id != camera.camera_id:
            existing_camera_with_new_id = await db.execute(
                select(models.Camera).filter(
                    models.Camera.camera_id == camera.camera_id
                )
            )
            if existing_camera_with_new_id.scalars().first() is not None:
                logger.error(
                    f"Camera with new camera_id {camera.camera_id} already exists"
                )
                raise HTTPException(
                    status_code=409, detail="Camera with new camera_id already exists"
                )

        existing_camera.camera_id = camera.camera_id
        existing_camera.rtsp_url = camera.rtsp_url
        existing_camera.area_selected_jpeg_path = camera.area_selected_jpeg_path
        existing_camera.area_selected_jpeg_width = camera.area_selected_jpeg_width
        existing_camera.area_selected_jpeg_height = camera.area_selected_jpeg_height
        existing_camera.selected_area_start_x = camera.selected_area_start_x
        existing_camera.selected_area_start_y = camera.selected_area_start_y
        existing_camera.selected_area_end_x = camera.selected_area_end_x
        existing_camera.selected_area_end_y = camera.selected_area_end_y

        await db.commit()
        logger.info(f"Camera with camera_id {camera_id} updated successfully")
        return existing_camera
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
        logger.error(f"Error updating camera with camera_id {camera_id}: {e}")
        await db.rollback()
        return None


async def delete_camera(db: AsyncSession, camera_id: str):
    logger.info(f"Deleting camera with camera_id {camera_id}")
    try:
        result = await db.execute(
            select(models.Camera).filter(models.Camera.camera_id == camera_id)
        )
        camera = result.scalar()
        if camera is None:
            logger.error(f"Camera with camera_id {camera_id} not found")
            return False

        await db.delete(camera)
        await db.commit()
        logger.info(f"Camera with camera_id {camera_id} deleted successfully")
        return True
    except Exception as e:
        logger.error(f"Error deleting camera with camera_id {camera_id}: {e}")
        await db.rollback()
        return False
