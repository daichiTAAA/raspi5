from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from api.db import get_db
from api.schemas.user import UserCreate
from api.setup_logger import setup_logger
import api.cruds as cruds

logger, log_decorator = setup_logger(__name__)

router_v1 = APIRouter(
    prefix="/users",
    tags=["User DB operations"],
    responses={404: {"description": "Not found"}},
)


@router_v1.post("")
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await cruds.get_user_by_user_id(db, user.user_id)
        if result is not None:
            logger.error(f"User {user.user_id} already registered")
            raise HTTPException(status_code=400, detail="User already registered")
        created_user = await cruds.create_user(db, user)
        logger.info(f"Created User: {created_user}")
        return created_user
    except HTTPException as e:
        if e.status_code == 400 and e.detail == "User already registered":
            logger.warning(
                f"Warnig error adding user {user.user_id} but ignore it: {e}"
            )
            return {"error": str(e)}
        else:
            logger.error(f"Error adding user {user.user_id}: {e}")
            raise e
    except Exception as e:
        logger.error(f"Error adding user {user.user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.get("")
async def get_users(db: AsyncSession = Depends(get_db)):
    try:
        users = await cruds.get_users(db)
        logger.info(f"Users retrieved successfully")
        return users
    except HTTPException as e:
        logger.error(f"Error retrieving users: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error retrieving users: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.get("/{user_id}")
async def get_user_by_user_id(user_id: str, db: AsyncSession = Depends(get_db)):
    try:
        user = await cruds.get_user_by_user_id(db, user_id)
        if user is None:
            logger.error(f"User {user_id} not found")
            raise HTTPException(status_code=404, detail="User not found")
        logger.info(f"User {user_id} retrieved successfully")
        return user
    except HTTPException as e:
        logger.error(f"Error retrieving user {user_id}: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error retrieving user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.put("/{user_id}")
async def update_user(
    user_id: str,
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await cruds.get_user_by_user_id(db, user_id)
        if result is None:
            logger.error(f"User {user_id} not found")
            raise HTTPException(status_code=404, detail="User not found")
        updated_user = await cruds.update_user(db, user_id, user)
        if updated_user is None:
            logger.error(f"Error updating user {user_id}")
            raise HTTPException(status_code=500, detail="Error updating user")
        logger.info(f"Updated User: {updated_user}")
        return updated_user
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
        logger.error(f"Error updating user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_v1.delete("/{user_id}")
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    try:
        user = await cruds.get_user_by_user_id(db, user_id)
        if user is None:
            logger.error(f"User {user_id} not found")
            raise HTTPException(status_code=404, detail="User not found")
        await cruds.delete_user(db, user_id)
        logger.info(f"User {user_id} deleted successfully")
        return {"message": f"User {user_id} deleted successfully"}
    except HTTPException as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
