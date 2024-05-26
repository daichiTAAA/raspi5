from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import api.models as models
import api.schemas as schemas
from api.setup_logger import setup_logger

logger, log_decorator = setup_logger(__name__)


async def get_users(db: AsyncSession):
    logger.info("Fetching all users")
    try:
        result = await db.execute(select(models.User))
        logger.info("Successfully fetched all users")
        return result.scalars().all()
    except Exception as e:
        logger.error(f"Error fetching all users: {e}")
        return None


async def get_user_by_user_id(db: AsyncSession, user_id: str):
    """ユーザーをuser_idで取得"""
    logger.info(f"Fetching user with user_id {user_id}")
    try:
        result = await db.execute(
            select(models.User).filter(models.User.user_id == user_id)
        )
        logger.info(f"Successfully fetched user with user_id {user_id}")
        return result.scalars().first()
    except Exception as e:
        logger.error(f"Error fetching user with user_id {user_id}: {e}")
        return None


async def create_user(db: AsyncSession, user: schemas.UserCreate) -> models.User | None:
    logger.info(f"Creating user with user_id {user.user_id}")
    try:
        new_user = models.User(
            user_id=user.user_id,
            camera_id=user.camera_id,
            rtsp_url=user.rtsp_url,
            wss_url=user.wss_url,
        )
        db.add(new_user)
        await db.commit()
        created_user: models.User = models.User(
            user_id=user.user_id,
            camera_id=user.camera_id,
            rtsp_url=user.rtsp_url,
            wss_url=user.wss_url,
        )
        logger.info(f"User with user_id {user.user_id} created successfully")
        return created_user
    except Exception as e:
        logger.error(f"Error creating user with user_id {user.user_id}: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


async def update_user(
    db: AsyncSession, user_id: str, user: schemas.UserCreate
) -> models.User | None:
    logger.info(f"Updating user with user_id {user_id}")
    try:
        result = await db.execute(
            select(models.User).filter(models.User.user_id == user_id)
        )
        existing_user = result.scalars().first()
        if existing_user is None:
            return None

        # Check if the new user_id already exists
        if user_id != user.user_id:
            existing_user_with_new_id = await db.execute(
                select(models.User).filter(models.User.user_id == user.user_id)
            )
            if existing_user_with_new_id.scalars().first() is not None:
                logger.error(f"User with new user_id {user.user_id} already exists")
                raise HTTPException(
                    status_code=409, detail="User with new user_id already exists"
                )

        existing_user.user_id = user.user_id
        existing_user.camera_id = user.camera_id
        existing_user.rtsp_url = user.rtsp_url
        existing_user.wss_url = user.wss_url
        await db.commit()
        logger.info(f"User with user_id {user_id} updated successfully")
        return existing_user
    except HTTPException as e:
        if e.status_code == 409 and e.detail == f"User with new user_id already exists":
            logger.warning(f"Conflict error updating user {user_id}: {e}")
            raise HTTPException(
                status_code=409,
                detail=f"User with new user_id already exists",
            )
        logger.error(f"Error updating user {user_id}: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error updating user with user_id {user_id}: {e}")
        await db.rollback()
        return None


async def delete_user(db: AsyncSession, user_id: str):
    logger.info(f"Deleting user with user_id {user_id}")
    try:
        result = await db.execute(
            select(models.User).filter(models.User.user_id == user_id)
        )
        user = result.scalar()
        if user is None:
            logger.error(f"User with user_id {user_id} not found")
            return False

        await db.delete(user)
        await db.commit()
        logger.info(f"User with user_id {user_id} deleted successfully")
        return True
    except Exception as e:
        logger.error(f"Error deleting user with user_id {user_id}: {e}")
        await db.rollback()
        return False
