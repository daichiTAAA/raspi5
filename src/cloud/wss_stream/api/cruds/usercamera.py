from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import api.models as models
import api.schemas as schemas
from api.setup_logger import setup_logger

logger, log_decorator = setup_logger(__name__)


async def get_usercameras(db: AsyncSession):
    logger.info("Fetching all usercameras")
    try:
        result = await db.execute(select(models.UserCamera))
        logger.info("Successfully fetched all usercameras")
        return result.scalars().all()
    except Exception as e:
        logger.error(f"Error fetching all usercameras: {e}")
        return None


async def get_usercamera_by_user_and_camera_id(
    db: AsyncSession, user_id: str, camera_id: str
):
    """ユーザーカメラをuser_idとcamera_idで取得"""
    logger.info(f"Fetching usercamera with user_id {user_id}, camera_id {camera_id}")
    try:
        result = await db.execute(
            select(models.UserCamera).filter(
                models.UserCamera.user_id == user_id,
                models.UserCamera.camera_id == camera_id,
            )
        )
        logger.info(
            f"Successfully fetched usercamera with user_id {user_id}, camera_id {camera_id}"
        )
        return result.scalars().first()
    except Exception as e:
        logger.error(
            f"Error fetching usercamera with user_id {user_id}, camera_id {camera_id}: {e}"
        )
        return None


async def create_usercamera(
    db: AsyncSession, usercamera: schemas.UserCameraCreate
) -> models.UserCamera | None:
    logger.info(
        f"Creating usercamera with user_id {usercamera.user_id}, camera_id {usercamera.camera_id}"
    )
    try:
        new_usercamera = models.UserCamera(
            user_id=usercamera.user_id,
            camera_id=usercamera.camera_id,
            rtsp_url=usercamera.rtsp_url,
        )
        db.add(new_usercamera)
        await db.commit()
        created_usercamera: models.UserCamera = models.UserCamera(
            user_id=usercamera.user_id,
            camera_id=usercamera.camera_id,
            rtsp_url=usercamera.rtsp_url,
        )
        logger.info(
            f"Usercamera with user_id {usercamera.user_id}, camera_id {usercamera.camera_id} created successfully"
        )
        return created_usercamera
    except Exception as e:
        logger.error(
            f"Error creating usercamera with user_id {usercamera.user_id}, camera_id {usercamera.camera_id}: {e}"
        )
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


async def update_usercamera(
    db: AsyncSession, user_id: str, camera_id: str, usercamera: schemas.UserCameraCreate
) -> models.UserCamera | None:
    logger.info(f"Updating usercamera with user_id {user_id}, camera_id {camera_id}")
    try:
        result = await db.execute(
            select(models.UserCamera).filter(
                models.UserCamera.user_id == user_id,
                models.UserCamera.camera_id == camera_id,
            )
        )
        existing_usercamera = result.scalars().first()
        if existing_usercamera is None:
            return None

        # Check if the new user_id already exists
        if user_id != usercamera.user_id:
            existing_usercamera_with_new_id = await db.execute(
                select(models.UserCamera).filter(
                    models.UserCamera.user_id == usercamera.user_id,
                    models.UserCamera.camera_id == usercamera.camera_id,
                )
            )
            if existing_usercamera_with_new_id.scalars().first() is not None:
                logger.error(
                    f"Usercamera with new user_id {usercamera.user_id}, camera_id {usercamera.camera_id} already exists"
                )
                raise HTTPException(
                    status_code=409,
                    detail="Usercamera with new user_id, camera_id already exists",
                )

        existing_usercamera.user_id = usercamera.user_id
        existing_usercamera.camera_id = usercamera.camera_id
        existing_usercamera.rtsp_url = usercamera.rtsp_url
        await db.commit()
        logger.info(
            f"Usercamera with user_id {user_id}, camera_id {camera_id} updated successfully"
        )
        return existing_usercamera
    except HTTPException as e:
        if (
            e.status_code == 409
            and e.detail == f"Usercamera with new user_id, camera_id already exists"
        ):
            logger.warning(
                f"Conflict error updating usercamera user_id {user_id}, camera_id {camera_id}: {e}"
            )
            raise HTTPException(
                status_code=409,
                detail=f"Usercamera with new user_id, camera_id already exists",
            )
        logger.error(
            f"Error updating usercamera user_id {user_id}, camera_id {camera_id}: {e}"
        )
        raise e
    except Exception as e:
        logger.error(
            f"Error updating usercamera with user_id {user_id}, camera_id {camera_id}: {e}"
        )
        await db.rollback()
        return None


async def delete_usercamera(db: AsyncSession, user_id: str, camera_id: str):
    logger.info(f"Deleting usercamera with user_id {user_id}, camera_id {camera_id}")
    try:
        result = await db.execute(
            select(models.UserCamera).filter(
                models.UserCamera.user_id == user_id,
                models.UserCamera.camera_id == camera_id,
            )
        )
        usercamera = result.scalar()
        if usercamera is None:
            logger.error(
                f"Usercamera with user_id {user_id}, camera_id {camera_id} not found"
            )
            return False

        await db.delete(usercamera)
        await db.commit()
        logger.info(
            f"Usercamera with user_id {user_id}, camera_id {camera_id} deleted successfully"
        )
        return True
    except Exception as e:
        logger.error(
            f"Error deleting usercamera with user_id {user_id}, camera_id {camera_id}: {e}"
        )
        await db.rollback()
        return False
