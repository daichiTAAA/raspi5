from fastapi import APIRouter, Depends, WebSocket

from api.services.usercamera_service import UserCameraService
from api.setup_logger import setup_logger

logger, log_decorator = setup_logger(__name__)

router_v1 = APIRouter(
    prefix="/wsss",
    tags=["Wss operations"],
    responses={404: {"description": "Not found"}},
)


@router_v1.websocket("/ws/{user_id}/{camera_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
    camera_id: str,
    usercamera_service: UserCameraService = Depends(UserCameraService),
):
    logger.info(
        f"Starting websocket connection for user_id: {user_id}, camera_id: {camera_id}"
    )
    await usercamera_service.start_wss_stream_process(websocket, user_id, camera_id)
