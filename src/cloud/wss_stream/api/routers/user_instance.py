from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from api.db import get_db
from api.services.user_service import UserService
from api.setup_logger import setup_logger
import api.cruds as cruds

logger, log_decorator = setup_logger(__name__)

router_v1 = APIRouter(
    prefix="/userinstances",
    tags=["User instance operations"],
    responses={404: {"description": "Not found"}},
)


@router_v1.post("/{user_id}")
async def create_user_instance(
    user_id: str,
    user_service: UserService = Depends(),
    db: AsyncSession = Depends(get_db),
):
    result = await cruds.get_user_by_user_id(db, user_id)
    if result is None:
        logger.error(f"User {user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")
    rtsp_url = result.rtsp_url
    try:
        user_service.create_user_instance(user_id, rtsp_url)
        logger.info(f"User instance created for user {user_id}")
        return {"message": f"User instance created for user {user_id}"}
    except HTTPException as e:
        logger.error(f"Error creating user instance for user {user_id}: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error creating user instance for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.get("")
def get_user_instances(user_service: UserService = Depends()):
    try:
        user_instances = user_service.get_user_instances()
        logger.info(f"User instances retrieved")
        return user_instances
    except HTTPException as e:
        logger.error(f"Error retrieving user instances: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error retrieving user instances: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.get("/{user_id}")
def get_user_instance_by_user_id(user_id: str, user_service: UserService = Depends()):
    try:
        user_instance = user_service.get_user_instance_by_user_id(user_id)
        logger.info(f"User instance retrieved for user {user_id}")
        return user_instance
    except HTTPException as e:
        logger.error(f"Error retrieving user instance for user {user_id}: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error retrieving user instance for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.delete("/{user_id}")
def delete_user_instance(user_id: str, user_service: UserService = Depends()):
    try:
        user_service.delete_user_instance(user_id)
        logger.info(f"User instance deleted for user {user_id}")
        return {"message": f"User instance deleted for user {user_id}"}
    except HTTPException as e:
        logger.error(f"Error deleting user instance for user {user_id}: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error deleting user instance for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
