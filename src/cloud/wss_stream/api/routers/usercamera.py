from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from api.db import get_db
from api.schemas.usercamera import UserCameraCreate
from api.setup_logger import setup_logger
import api.cruds as cruds


logger, log_decorator = setup_logger(__name__)

router_v1 = APIRouter(
    prefix="/usercameras",
    tags=["Usercamera DB operations"],
    responses={404: {"description": "Not found"}},
)


@router_v1.post("")
async def create_usercamera(
    usercamera: UserCameraCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await cruds.get_usercamera_by_user_and_camera_id(
            db, usercamera.user_id, usercamera.camera_id
        )
        if result is not None:
            logger.error(
                f"Usercamera user_id {usercamera.user_id}, camera_id {usercamera.camera_id} already registered"
            )
            raise HTTPException(status_code=400, detail="Usercamera already registered")
        created_usercamera = await cruds.create_usercamera(db, usercamera)
        logger.info(f"Created User: {created_usercamera}")
        return created_usercamera
    except HTTPException as e:
        if e.status_code == 400 and e.detail == "Usercamera already registered":
            logger.warning(
                f"Warnig error adding usercamera user_id {usercamera.user_id}, camera_id {usercamera.camera_id} but ignore it: {e}"
            )
            return {"error": str(e)}
        else:
            logger.error(
                f"Error adding usercamera user_id {usercamera.user_id}, camera_id {usercamera.camera_id}: {e}"
            )
            raise e
    except Exception as e:
        logger.error(
            f"Error adding usercamera user_id {usercamera.user_id}, camera_id {usercamera.camera_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.get("")
async def get_usercameras(db: AsyncSession = Depends(get_db)):
    try:
        usercameras = await cruds.get_usercameras(db)
        logger.info(f"Users retrieved successfully")
        return usercameras
    except HTTPException as e:
        logger.error(f"Error retrieving usercameras: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error retrieving usercameras: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.get("/{user_id}/{camera_id}")
async def get_usercamera_by_user_and_camera_id(
    user_id: str, camera_id: str, db: AsyncSession = Depends(get_db)
):
    try:
        usercamera = await cruds.get_usercamera_by_user_and_camera_id(
            db, user_id, camera_id
        )
        if usercamera is None:
            logger.error(
                f"Usercamera user_id:{user_id}, camera_id:{camera_id} not found"
            )
            raise HTTPException(status_code=404, detail="Usercamera not found")
        logger.info(f"Usercamera user_id:{user_id}, camera_id:{camera_id} retrieved")
        return usercamera
    except HTTPException as e:
        logger.error(
            f"Error retrieving usercamera user_id:{user_id}, camera_id:{camera_id}: {e}"
        )
        raise e
    except Exception as e:
        logger.error(
            f"Error retrieving usercamera user_id:{user_id}, camera_id:{camera_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.put("/{user_id}/{camera_id}")
async def update_usercamera(
    user_id: str,
    camera_id: str,
    usercamera: UserCameraCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await cruds.get_usercamera_by_user_and_camera_id(
            db, user_id, camera_id
        )
        if result is None:
            logger.error(
                f"Usercamera user_id {user_id}, camera_id {camera_id} not found"
            )
            raise HTTPException(status_code=404, detail="Usercamera not found")
        updated_usercamera = await cruds.update_usercamera(
            db, user_id, camera_id, usercamera
        )
        if updated_usercamera is None:
            logger.error(
                f"Error updating usercamera user_id {user_id}, camera_id {camera_id}"
            )
            raise HTTPException(status_code=500, detail="Error updating usercamera")
        logger.info(
            f"Usercamera user_id {user_id}, camera_id {camera_id} updated successfully"
        )
        return updated_usercamera
    except HTTPException as e:
        if (
            e.status_code == 409
            and e.detail == f"Usercamera with new user_id, camera_id already exists"
        ):
            logger.warning(
                f"Conflict error updating usercamera user_id:{user_id}, camera_id:{camera_id}: {e}"
            )
            raise HTTPException(
                status_code=409,
                detail=f"Usercamera with new user_id, camera_id already exists",
            )
        logger.error(
            f"Error updating usercamera user_id:{user_id}, camera_id:{camera_id}: {e}"
        )
        raise e
    except Exception as e:
        logger.error(
            f"Error updating usercamera user_id:{user_id}, camera_id:{camera_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.delete("/{user_id}/{camera_id}")
async def delete_usercamera(
    user_id: str,
    camera_id: str,
    db: AsyncSession = Depends(get_db),
):
    try:
        usercamera = await cruds.get_usercamera_by_user_and_camera_id(
            db, user_id, camera_id
        )
        if usercamera is None:
            logger.error(
                f"Usercamera user_id {user_id}, camera_id {camera_id} not found"
            )
            raise HTTPException(status_code=404, detail="Usercamera not found")
        await cruds.delete_usercamera(db, user_id, camera_id)
        logger.info(
            f"Usercamera user_id {user_id}, camera_id {camera_id} deleted successfully"
        )
        return {
            "message": f"Usercamera user_id {user_id}, camera_id {camera_id} deleted successfully"
        }
    except HTTPException as e:
        logger.error(
            f"Error deleting usercamera user_id:{user_id}, camera_id:{camera_id}: {e}"
        )
        raise e
    except Exception as e:
        logger.error(
            f"Error deleting usercamera user_id:{user_id}, camera_id:{camera_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=str(e))
