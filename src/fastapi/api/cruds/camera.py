from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import api.models as models
import api.schemas as schemas
from api.setup_logger import setup_logger

logger, log_decorator = setup_logger(__name__)


# カメラをcamera_idで取得
async def get_camera_by_camera_id(db: AsyncSession, camera_id: str):
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
